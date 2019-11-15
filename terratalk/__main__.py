import os
import re
import subprocess

import click

from terratalk.bitbucket_server import BitbucketServer
from terratalk.terraform import Terraform


@click.group()
def cli():
    pass


@cli.command()
@click.option('-s', '--server')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-w', '--workspace')
@click.option('--project-key')
@click.option('--repository-slug')
@click.option('--pull-request-id')
def comment(server, username, password, workspace, project_key, repository_slug, pull_request_id):

    if server is None and project_key is None and repository_slug is None and pull_request_id is None and os.getenv('CHANGE_URL') is not None:
        m = re.match(r'\A(https?://.*?)/projects/([^/]+)/repos/([^/]+)/pull-requests/(\d+)', os.getenv('CHANGE_URL'), re.IGNORECASE)
        server = m.group(1)
        project_key = m.group(2)
        repository_slug = m.group(3)
        pull_request_id = m.group(4)

    if username is None and os.getenv('STASH_USER') is not None:
        username = os.getenv('STASH_USER')

    if password is None and os.getenv('STASH_PASS') is not None:
        password = os.getenv('STASH_PASS')

    bs = BitbucketServer(base_url=server, username=username, password=password)
    bs.pr(project_key=project_key, repository_slug=repository_slug, pull_request_id=pull_request_id)

    # delete any older comments
    for comment in bs.comments():
        if comment['comment']['text'].lstrip().startswith(f'[comment]: # (terratalk: {workspace})'):
            click.echo('[terratalk] deleting comment {comment_id}'.format(comment_id=comment['id']))
            bs.comment_delete(comment['comment']['id'], comment['comment']['version'])

    # fetch terraform output
    tf = Terraform()
    plan_output = tf.show(workspace + '.plan')

    if plan_output == '' or plan_output.lstrip().startswith('This plan does nothing.'):
        print('[terratalk] this plan does nothing')
        exit()

    # https://bitbucket.org/tutorials/markdowndemo/issues/15/how-can-you-insert-comments-in-the#comment-22433250
    bs.comment_add(f'''
[comment]: # (terratalk: {workspace})
### tf plan output: {workspace}
```
{plan_output}
```
''')


@cli.command()
@click.option('-w', '--workspace')
def output(workspace):
    tf = Terraform()
    plan_output = tf.show(workspace + '.plan')

    if plan_output == '' or plan_output.lstrip().startswith('This plan does nothing.'):
        print('[terratalk] this plan does nothing')
    else:
        print(plan_output)


if __name__ == '__main__':
    cli()
