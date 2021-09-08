#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ssl
from functools import wraps
import argparse
import json
from time import sleep
from github import Github


def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar


ssl.wrap_socket = sslwrap(ssl.wrap_socket)


# Assignees must have push access to repo. Otherwise, the process
# will be interrupted.
#
# The ".DEFAULT" assignee is used when the assignee in Bitbucket no
# longer exists in Github. I.e, for inactive commiters. Default commiter
# can be None.
#
# The structure of this dict is:
# ASSIGNEES = {'bitbucket_user': 'github_user'}

ASSIGNEES = {'.DEFAULT': 'default_committer',
             }


# Github doesn't have all statuses as Bitbucket.
# So, we use labels to identify issues.

BITBUCKET_STATUSES_THAT_ARE_GITHUB_LABELS = [
    'on hold', 'duplicate', 'invalid', 'wontfix']


# Status equivalence between services.

GITHUB_OPEN_STATE = 'open'
GITHUB_CLOSED_STATE = 'closed'
BITBUCKET_STATUSES_MAPPED_TO_GITHUB = {
    'new': GITHUB_OPEN_STATE,
    'open': GITHUB_OPEN_STATE,
    'resolved': GITHUB_CLOSED_STATE,
    'on hold': GITHUB_OPEN_STATE,
    'invalid': GITHUB_CLOSED_STATE,
    'duplicate': GITHUB_CLOSED_STATE,
    'wontfix': GITHUB_CLOSED_STATE
}


def _parse_args():
    """Create and parse command line args."""

    argparser = argparse.ArgumentParser(
        description='Import BitBucket issues into Github.')
    argparser.add_argument(
        'file', help='JSON file with BitBucket exported data')
    argparser.add_argument(
        '-t', '--token', required=True,
        help='Github access token')
    argparser.add_argument(
        '-r', '--repo', required=True,
        help='Github repo where issues will imported (required)')
    argparser.add_argument(
        '-u', '--user', dest='username',
        help=('Github user who repo belongs to. '
              'If ommited, --login used.'))
    argparser.add_argument(
        '--start-from', dest='startfrom', default="",
        help=('Ignore issues whose title compares less than this.')
    )
    argparser.add_argument(
        '--no-assignees', dest='consider_assignees',
        action='store_const', const=False, default=True,
        help='You will not use assignees in issues.')

    argv = argparser.parse_args()
    if not argv.username:
        argv.username = argv.login
    return argv


def import_issue(repo, bitbucket_data, argv):
    """Import a single issue."""

    comment_message = []

    # print("=" * 50)
    # print("Issue {id}".format(**bitbucket_data))
    # print("Bitbucket data")
    # print("--------------")
    # print(bitbucket_data)
    print('\n')
    print('* Importing issue {id}'.format(**bitbucket_data))

    labels = ['imported',  # you'll know what issues were imported.
              bitbucket_data['kind'],
              bitbucket_data['priority']]
    if bitbucket_data['component']:
        labels.append(bitbucket_data['component'])

    if (bitbucket_data['status'] in
            BITBUCKET_STATUSES_THAT_ARE_GITHUB_LABELS):
        labels.append(bitbucket_data['status'])

    if bitbucket_data['assignee'] and argv.consider_assignees:
        if bitbucket_data['assignee'] in ASSIGNEES:
            assignee = ASSIGNEES[bitbucket_data['assignee']]
        else:
            assignee = ASSIGNEES['.DEFAULT']
            comment_message.append(
                '(Original issue was assigned to {assignee})'
                ''.format(**bitbucket_data))
    else:
        assignee = None

    issue_body = '\n\n'.join([
        '(Original issue {id} created by {reporter} on {created_on})',
        '{content}']
    ).format(**bitbucket_data)

    github_data = {
        'title': bitbucket_data['title'],
        'body': issue_body,
        'labels': labels,
    }

    if assignee:
        github_data['assignee'] = assignee


    # print("Github data")
    # print("-----------")
    # print(github_data)

    github_issue = repo.create_issue(**github_data)
    sleep(3)

    print('Imported as {github_issue}'.format(github_issue=github_issue))

    if BITBUCKET_STATUSES_MAPPED_TO_GITHUB.get(
            bitbucket_data['status']) == GITHUB_CLOSED_STATE:
        comment_message.append(
            '(Original issue {id} last updated on {updated_on})'
            ''.format(**bitbucket_data))
        comment_message.append(
            '(Issue automatically closed due to status in Bitbucket: '
            '{status})'
            ''.format(**bitbucket_data))

        github_issue.edit(state=GITHUB_CLOSED_STATE)
        print('Closed')

    if comment_message:
        github_issue.create_comment("\n".join(comment_message))

    return github_issue


def import_comment(github_issue, comment, argv):
    """Import a single comment."""

    if not comment['content']:
        # ignores status changing comments.
        return

    github_issue.create_comment(
        '(Original comment by {user} on {created_on})\n\n'
        '{content}\n\n'.format(**comment))


def import_issues_and_comments(repo, issues, comments, argv):
    issues_read = issues_imported = 0
    comments_read = comments_imported = 0

    issues = sorted(issues, key=lambda x: x['id'])

    for bitbucket_issue in issues:
        issues_read += 1

        if bitbucket_issue["title"] <= argv.startfrom:
            print(f"Skipping {bitbucket_issue['title']}")
            continue

        github_issue = import_issue(repo, bitbucket_issue, argv=argv)
        issues_imported += 1

        # get comments for this issue
        issue_comments = [c for c in comments if c['issue'] ==
                          bitbucket_issue['id']]
        # sort to insert comments in creation order.
        issue_comments = sorted(issue_comments,
                                key=lambda x: x['id'])

        for bitbucket_comment in issue_comments:
            comments_read += 1
            # delay comment insertion to order comments properly.
            sleep(1)
            import_comment(
                github_issue=github_issue,
                comment=bitbucket_comment,
                argv=argv)
            comments_imported += 1

    return {
        'issues_read': issues_read,
        'issues_imported': issues_imported,
        'comments_read': comments_read,
        'comments_imported': comments_imported
    }


def main():
    argv = _parse_args()

    if argv.consider_assignees:
        if (ASSIGNEES.get('.DEFAULT') == 'default_committer'
                and len(ASSIGNEES) == 1):
            print('Set ASSIGNEES dict, or inform --no-assignees option '
                  'to ignore it.')
            exit(1)
    else:
        ASSIGNEES['.DEFAULT'] = None

    with open(argv.file) as f:
        bitbucket_data = json.load(f)

    gh = Github(argv.token)
    repo = gh.get_repo(argv.username + "/" + argv.repo)

    ret = import_issues_and_comments(
        repo=repo,
        issues=bitbucket_data['issues'][:],
        comments=bitbucket_data['comments'],
        argv=argv)

    print("""
Done.

Import overview
===============

Issues:
    read: {issues_read}
    imported: {issues_imported}
Comments:
    read: {comments_read}
    imported: {comments_imported}
""".format(**ret)
          )


if __name__ == '__main__':
    main()
