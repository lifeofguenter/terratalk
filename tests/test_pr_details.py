import os
from unittest import TestCase, mock

from terratalk.pr_details import PrDetails


class TestMain(TestCase):

    @mock.patch.dict(os.environ, {
        'CI_SERVER_NAME': 'GitLab',
        'CI_MERGE_REQUEST_IID': '8',
        'CI_MERGE_REQUEST_PROJECT_ID': '428',
        'CI_SERVER_URL': 'https://gitlab.company.com',
    })
    def test_gitlab(self):
        pr = PrDetails()

        self.assertEqual(pr.type, 'gitlab')
        self.assertEqual(pr.server, 'https://gitlab.company.com')
        self.assertEqual(pr.project_key, 428)
        self.assertEqual(pr.pull_request_id, 8)

    @mock.patch.dict(os.environ, {
        'CHANGE_URL': 'https://github.com/test-org/test-repo/pull/6',
    })
    def test_github(self):
        pr = PrDetails()

        self.assertEqual(pr.type, 'github')
        self.assertEqual(pr.server, 'github.com')
        self.assertEqual(pr.project_key, 'test-org')
        self.assertEqual(pr.repository_slug, 'test-repo')
        self.assertEqual(pr.pull_request_id, 6)

    @mock.patch.dict(os.environ, {
        'CHANGE_URL': 'https://bitbucket.org/test-org/test-repo/pull-requests/33',
    })
    def test_bitbucket(self):
        pr = PrDetails()

        self.assertEqual(pr.type, 'bitbucket')
        self.assertEqual(pr.server, 'bitbucket.org')
        self.assertEqual(pr.project_key, 'test-org')
        self.assertEqual(pr.repository_slug, 'test-repo')
        self.assertEqual(pr.pull_request_id, 33)

    @mock.patch.dict(os.environ, {
        'CHANGE_URL': 'https://stash.com/projects/FOO/repos/foobar/pull-requests/186',
    })
    def test_bitbucket_server(self):
        pr = PrDetails()

        self.assertEqual(pr.type, 'bitbucket-server')
        self.assertEqual(pr.server, 'https://stash.com')
        self.assertEqual(pr.project_key, 'FOO')
        self.assertEqual(pr.repository_slug, 'foobar')
        self.assertEqual(pr.pull_request_id, 186)
