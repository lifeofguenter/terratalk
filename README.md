# terratalk

[![build and publish](https://github.com/lifeofguenter/terratalk/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/lifeofguenter/terratalk/actions/workflows/build-and-publish.yml)
[![Coverage Status](https://coveralls.io/repos/github/lifeofguenter/terratalk/badge.svg)](https://coveralls.io/github/lifeofguenter/terratalk)
[![PyPI](https://img.shields.io/pypi/v/terratalk.svg)](https://pypi.org/project/terratalk/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/terratalk)
[![License](https://img.shields.io/github/license/lifeofguenter/terratalk.svg)](LICENSE)

**_Terratalk_** is a simple tool to add an opinionated terraform plan output
into your pull-request as a comment. This allows you to have a quick feedback on
infrastructure changes without having to leave the context of your pull-request
view.

## Setup

### Prerequisite

This tool relies on either
[Bitbucket Branch Source](https://plugins.jenkins.io/cloudbees-bitbucket-branch-source/)
or [GitHub Branch Source](https://plugins.jenkins.io/github-branch-source/) to
be installed as a plugin on your Jenkins. Alternatively you can set the
environment variable `CHANGE_URL` to the URL of the pull-request which will
allow `terratalk` to construct the proper API request to your SCM.

GitLab is currently only supported from gitlab-pipelines.

### Installation

On the build agent, install `terratalk`:

```bash
$ pip install --user terratalk
```

If you are using GitHub you will additionally need to install the following:

```bash
$ pip install --user PyGithub
```

If you are using GitLab you will additionally need to install the following:

```bash
$ pip install --user python-gitlab
```

### Running

Execute in the same directory, optionally with the same `TF_DATA_DIR` as you
would normally run `terraform`. If you use
[`tfenv`](https://github.com/tfutils/tfenv) that will work as well.

```bash
$ terraform plan -out WORKSPACE.plan
$ terratalk comment -w WORKSPACE
```

### Supported environment variables

#### Bitbucket Server

* `STASH_USER`
* `STASH_PASS`

#### Bitbucket Cloud

* `BITBUCKET_USERNAME`
* `BITBUCKET_APP_PASSWORD`

#### GitHub

* `GITHUB_TOKEN`

#### GitLab

* `GITLAB_TOKEN`

## Results

![terratalk on Bitbucket Server](https://raw.githubusercontent.com/lifeofguenter/terratalk/main/docs/images/terratalk-on-bitbucket-server.png "terratalk on Bitbucket Server")

## License

[MIT](LICENSE)
