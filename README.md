# bb2gh

The bb2gh package is a python module for translating Bitbucket issue
into Github issues.

## Installation

Use

    $ python setup.py install

to install, be sure to have https://github.com/jacquev6/PyGithub.

## Usage

Create a yaml file of the form.

```
bitbucket:
  repo: repo_name
  user: user_name
github:
  repo: repo_name
  user: user_name
tokens:
  default: xxx
  user1: xxx
  user2: xxx
```

The default token corresponds to the token for the main Github
user. Tokens for other users can be added so that issues and comment
reporters are added correctly. The user names refer to the Bitbucket
user names.

To run the migration use

    >>> import bb2gh
    >>> config_yaml = 'config.yaml'
    >>> bb2gh.migrate(config_yaml, verbose=True)

To only run a subset of the tickets use

    >>> bb2gh.migrate(config_yaml, verbose=True, issue_ids=[1, 3, 5])

where `issue_ids` refer to the Bitbucket ticket IDs.

