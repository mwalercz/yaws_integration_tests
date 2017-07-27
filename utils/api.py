from time import sleep
from urllib.parse import urljoin

import requests


class BrokerApiClient:
    def __init__(self, broker_url):
        self.broker_url = broker_url

    def make_request(self, method, path, headers=None, json=None):
        url = urljoin(self.broker_url, path)
        headers = headers or {'username': 'test', 'password': 'test'}

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            verify=False,
            json=json
        )

    def make_request_until(
            self, method, path, fun, headers=None,
            json=None, timeout=10, delay=1
    ):
        for i in range(0, int(timeout / delay)):
            response = self.make_request(method, path, headers, json)
            if fun(response):
                return response
            sleep(delay)

        raise Exception('Timeout!')

    def get_user_work_after_finish_with_success(self, work_id, user='test', timeout=5):
        return self.make_request_until(
            method='GET',
            path='/users/{user}/works/{work_id}'.format(
                user=user,
                work_id=work_id,
            ),
            fun=lambda response: response.json()['work']['status'] == (
                'finished_with_success'
            ),
            timeout=timeout,
        )

    def post_user_work(self, command, cwd='/home/test', user='test'):
        response = self.make_request(
            'POST',
            '/users/{user}/works'.format(user=user),
            json={
                'command': command,
                'cwd': cwd,
                'env': {},
            }
        )
        assert response.status_code == 202
        return response.json()['work_id']

    def get_user_works(self, user='test'):
        return self.make_request(
            'GET',
            '/users/{user}/works'.format(user=user)
        )

    def get_user_work(self, work_id, user='test'):
        return self.make_request(
            'GET',
            '/users/{user}/works/{work_id}'.format(
                user=user,
                work_id=work_id
            )
        ).json()['work']
