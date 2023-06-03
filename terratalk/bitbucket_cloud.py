import requests
from time import sleep


class BitbucketCloud:
    BASE_URL = 'https://api.bitbucket.org/2.0'

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.project_key = None
        self.repository_slug = None
        self.pull_request_id = None

    def pr(self, project_key=None, repository_slug=None, pull_request_id=None):
        self.project_key = project_key
        self.repository_slug = repository_slug
        self.pull_request_id = pull_request_id

    def comments(self):
        request_url = f'{self.BASE_URL}/repositories/{self.project_key}/' \
                      f'{self.repository_slug}/pullrequests/' \
                      f'{self.pull_request_id}/comments'
        comments = []

        for comment in self.paginator(request_url):
            if not comment['deleted']:
                comments.append(comment)

        return comments

    def comment_add(self, comment: str):
        request_url = f'{self.BASE_URL}/repositories/{self.project_key}/' \
                      f'{self.repository_slug}/pullrequests/' \
                      f'{self.pull_request_id}/comments'

        r = requests.post(
            request_url,
            json={'content': {'raw': comment}},
            auth=(self.username, self.password),
        )
        return r

    def comment_delete(self, comment_id):
        request_url = f'{self.BASE_URL}/repositories/{self.project_key}/' \
                      f'{self.repository_slug}/pullrequests/' \
                      f'{self.pull_request_id}/comments/{comment_id}'

        r = requests.delete(
            request_url,
            auth=(self.username, self.password),
        )
        return r

    def paginator(self, url, params=None):
        if params is None:
            params = {}

        values = []
        retries = 0

        buf = {'next': url}
        while 'next' in buf:
            r = requests.get(
                buf['next'],
                params=params,
                auth=(self.username, self.password),
            )

            buf = r.json()

            if 'values' not in buf and retries < 3:
                print(buf)
                retries = retries + 1
                sleep(1)
                continue

            values += buf['values']

            retries = 0

        return values
