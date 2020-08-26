import os
import re

import click

from terratalk.terraform import Terraform


@click.group()
def cli():
    pass


@cli.command()
@click.option('-w', '--workspace')
def comment(workspace):

    m = re.search(r'\Ahttps://github.com/([^/]+)/([^/]+)/pull/(\d+)\Z', os.getenv('CHANGE_URL'), re.IGNORECASE)
    if not m:
        m = re.search(r'\A(https?://.*?)/projects/([^/]+)/repos/([^/]+)/pull-requests/(\d+)', os.getenv('CHANGE_URL'), re.IGNORECASE)

    if len(m.groups()) == 3:
        server = 'github'
        project_key = m.group(1)
        repository_slug = m.group(2)
        pull_request_id = int(m.group(3))

    else:
        server = m.group(1)
        project_key = m.group(2)
        repository_slug = m.group(3)
        pull_request_id = int(m.group(4))

    if server == 'github':
        from github import Github

        gh = Github(os.getenv('GITHUB_TOKEN'))

        repo = gh.get_repo(f'{project_key}/{repository_slug}')
        issue = repo.get_issue(pull_request_id)

        # delete any older comments
        for c in issue.get_comments():
            if c.body.lstrip().startswith(f'<!-- terratalk: {workspace} -->'):
                click.echo(f'[tf-comment-plan] deleting previous comment: {c.id}')
                c.delete()

    else:
        from terratalk.bitbucket_server import BitbucketServer

        bs = BitbucketServer(base_url=server, username=os.getenv('STASH_USER'), password=os.getenv('STASH_PASS'))
        bs.pr(project_key=project_key, repository_slug=repository_slug, pull_request_id=pull_request_id)

        # delete any older comments
        for c in bs.comments():
            if c['comment']['text'].lstrip().startswith(f'[comment]: # (terratalk: {workspace})'):
                click.echo(f"[terratalk] deleting previous comment {c['id']}")
                bs.comment_delete(c['comment']['id'], c['comment']['version'])

    # fetch terraform output
    tf = Terraform()
    plan_output = tf.show(workspace + '.plan')

    if plan_output == '':
        click.echo('[terratalk] this plan does nothing')
        exit()

    if server == 'github':
        issue.create_comment(f'''
<!-- terratalk: {workspace} -->
### tf plan output: {workspace}
```
{plan_output}
```
''')

    else:
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

    if plan_output == '':
        click.echo('[terratalk] this plan does nothing')
    else:
        click.echo(plan_output)


if __name__ == '__main__':
    cli()
