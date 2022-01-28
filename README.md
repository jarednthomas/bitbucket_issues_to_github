
# Migrate Bitbucket issues to Github

Migrate Bitbucket issues to Github, with comments.

Issues are imported via the [Python wrapper for Github API v3](https://github.com/copitux/python-github3).

A `Personal Access Token` is needed to authenticate with Github. You can create an access token at the link [here](https://github.com/settings/tokens). 
More information about access tokens can be found in [github's documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). 


## Installation
------------

1. Create a python virtualenv and activate it:

```
python3 -m venv ./py3-env && cd py3-env/
source ./bin/activate
```

2. Clone this repo into the virtualenv:

```
git clone https://github.com/jarednthomas/bitbucket_issues_to_github
cd bitbucket_issues_to_github
```

3. Within this cloned repo, install python dependencies: 

```
pip3 install -r requirements.txt
```

## Configuration
------------

4. Edit the ASSIGNEES section of `bb2gh_issues.py` to preserve original asignees. Examples below and in source code.

Example Import
-------

```
$ python3 bb2gh_issues.py --user <repo_owner> --token <github_token> --repo <repo_name> db-1.0.json
```


Notes and Limitations
---------------------------

- You must first [export your issues in Bitbucket](https://confluence.atlassian.com/display/BITBUCKET/Export+or+Import+Issue+Data). The result will be one or more `.json` files similar to the one in the example above.

- Issues import cannot be undone. Run this process in a test repository before importing them to your real repo.

- All issues imported to Github will have the user authenticated via `--token` as the creator and the commenter. Each issue and comment will have a note to tell you who and when created the issue (or comment).

- You can preserve issues' assignees. Edit `bb2gh_issues.py` and change the `ASSIGNEES` dict to represent `'bitbucket username': 'github username'`

- Depending on how many issues and comments you have, this process can take a while.

- Milestones and images are not imported.


Options explained
-----------------

1. `-u`, `--user`

    The username that owns the repo. The username that appears
    in the repo url: (https://github.com/**this_username**/repo_name) -> 'this_username'

1. `-t`, `--token`

    [Github access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

1. `-r`, `--repo`

    Destination repository. The repository that will receive the issues: (https://github.com/username/**this_repo_name**) -> 'this_repo_name'

1. `--no-assignees`

    Don't use assignee information.

1. `file`

    The JSON file name with Bitbucket exported issues.
