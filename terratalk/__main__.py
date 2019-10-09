import click

import subprocess

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


if __name__ == '__main__':
    cli()
