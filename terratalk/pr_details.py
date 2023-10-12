import re
from os import getenv


class PrDetails:

    def __init__(self) -> None:
        self.type = None
        self.server = None
        self.project_key = None
        self.pull_request_id = None
        self.repository_slug = None

        self._resolve()

    def _resolve(self) -> None:
        if getenv('CI_SERVER_NAME') == 'GitLab':
            self.type = 'gitlab'
            self.server = getenv('CI_SERVER_URL')
            self.project_key = int(getenv('CI_MERGE_REQUEST_PROJECT_ID'))
            self.pull_request_id = int(getenv('CI_MERGE_REQUEST_IID'))
            return

        m = re.search(
            r'\A(https?://.*?)/projects/([^/]+)/repos/([^/]+)'
            r'/pull-requests/(\d+)',
            getenv('CHANGE_URL', ''),
            re.IGNORECASE,
        )
        if m:
            self.type = 'bitbucket-server'
            self.server = m.group(1)
            self.project_key = m.group(2)
            self.repository_slug = m.group(3)
            self.pull_request_id = int(m.group(4))
            return

        m = re.search(
            r'\Ahttps://(github\.com|bitbucket\.org)'
            r'/([^/]+)/([^/]+)/(?:pull|pull-requests)/(\d+)\Z',
            getenv('CHANGE_URL', ''),
            re.IGNORECASE,
        )
        if m:
            self.server = m.group(1)
            if self.server == 'github.com':
                self.type = 'github'
            else:
                self.type = 'bitbucket'
            self.project_key = m.group(2)
            self.repository_slug = m.group(3)
            self.pull_request_id = int(m.group(4))
            return
