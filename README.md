
Migrate Bitbucket issues to Github
==================================

Migrate Bitbucket issues to Github, with comments.

We use the [Python wrapper for Github API v3](https://github.com/copitux/python-github3) to achieve this.


Installation
------------

1. Create a python virtualenv and activate it.

```
python -m venv ./py3-env && cd py3-env/
source ./bin/activate
```

2. Clone this repo in the virtualenv
3. Install python dependencies 

```
pip install -r requirements.txt
```
4. Edit the ASSIGNEES section of `bb2gh_issues.py` accordingly

Example Import
-------

```
$ python bb2gh_issues.py --user <repo_owner> --token <github_token> --repo <repo_name> db-1.0.json
```


Notes and known limitations
---------------------------

You must [export your issues in Bitbucket](https://confluence.atlassian.com/display/BITBUCKET/Export+or+Import+Issue+Data), first.

Issues import cannot be undone. So, I suggest you to run this process in a test repository before importing them to your real one.


All issues created on Github will have your `--login` user as the creator and the commenter. So, each issue and comment will have a note to tell you who and when created the issue (or comment).

You can preserve issues' assignees. Edit `bb2gh_issues.py` and change the `ASSIGNEES` dict to represent your situation. Read comments on source code.

Depending on how many issues and comments you have, this process can take a while. Don't panic.

We don't import milestones or images. Pull requests are welcome. :-)


Options explained
-----------------

1. `-l`, `--login`

    You need to be logged in to create issues in Github. This is the
    username will be the creator of all issues and comments in this process.

1. `-`, `--token`

    Github access token.

1. `-r`, `--repo`

    The repository will receive your issues.

1. `-u`, `--user`

    The username who owns the repo. Also known as the username that appears
    in the repo url. I.e.: http://github.com/**this_is_the_username**/reponame

    If ommited, `--login` will be used.

1. `--no-assignees`

    Don't use assignee information.

1. `file`

    The JSON file name with Bitbucket exported issues.
