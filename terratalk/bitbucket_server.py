import requests
import urllib.parse


class BitbucketServer:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password


    def pr(self, project_key=None, repository_slug=None, pull_request_id=None):
        self.project_key = project_key
        self.repository_slug = repository_slug
        self.pull_request_id = pull_request_id


    def comments(self):
        request_url = f'{self.base_url}/rest/api/1.0/projects/{self.project_key}/repos/{self.repository_slug}/pull-requests/{self.pull_request_id}/activities'
        comments = []
        for value in self.paginator(request_url):
            if value['action'] == 'COMMENTED':
                comments.append(value)

        return comments


    def comment_add(self, comment):
        request_url = f'{self.base_url}/rest/api/1.0/projects/{self.project_key}/repos/{self.repository_slug}/pull-requests/{self.pull_request_id}/comments'
        r = requests.post(request_url, json={'text': comment}, auth=(self.username, self.password))
        return r

    def comment_delete(self, comment_id, version):
        request_url = f'{self.base_url}/rest/api/1.0/projects/{self.project_key}/repos/{self.repository_slug}/pull-requests/{self.pull_request_id}/comments/{comment_id}'
        r = requests.delete(request_url, params={'version': version}, auth=(self.username, self.password))
        return r


    def paginator(self, url, params={}):
        values = []

        while True:
            print(f'{url}?{urllib.parse.urlencode(params)}')
            r = requests.get(url, params=params, auth=(self.username, self.password))
            buf = r.json()

            values += buf['values']

            if buf['isLastPage']:
                break
            else:
                params['start'] = buf['nextPageStart']

        return values
