import unittest

from terratalk.drivers.bitbucket_server_comment import BitbucketServer


class TestMain(unittest.TestCase):

    def test_pr(self):
        base_url = 'https://foobar.com'
        username = 'user'
        password = 'pass'
        project_key = 'FOOBAR'
        repository_slug = 'barfoo'
        pull_request_id = 11

        bs = BitbucketServer(base_url=base_url,
                             username=username,
                             password=password)

        bs.pr(
            project_key=project_key,
            repository_slug=repository_slug,
            pull_request_id=pull_request_id,
        )

        self.assertEqual(bs.base_url, f"{base_url}/rest/api/1.0")
        self.assertEqual(bs.username, username)
        self.assertEqual(bs.password, password)
        self.assertEqual(bs.project_key, project_key)
        self.assertEqual(bs.repository_slug, repository_slug)
        self.assertEqual(bs.pull_request_id, pull_request_id)
