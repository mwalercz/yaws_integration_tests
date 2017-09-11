from time import sleep
from urllib.parse import urljoin

import requests


class BrokerApiClient:
    TEST_USER_HEADERS = {'username': 'test', 'password': 'test'}
    ADMIN_USER_HEADERS = {'username': 'admin', 'password': 'admin'}

    def __init__(self, broker_url):
        self.broker_url = broker_url

    def make_request(self, method, path, headers=None, json=None):
        url = urljoin(self.broker_url, path)
        headers = headers or self.TEST_USER_HEADERS
        print(
            'Request to broker:\n'
            'url:: {}\n'
            'headers: {}\n'
            'method: {}\n'
            'json: {}\n'.format(
                url, headers, method, json
            )
        )
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            verify=False,
            json=json
        )
        print(
            'Response from broker:\n'
            'status: {}\n'
            'text: {}\n'.format(response.status_code, response.text)
        )
        return response

    def make_request_with_retries(self, method, path, headers=None, json=None, timeout=10, delay=1):
        for i in range(0, int(timeout / delay)):
            try:
                return self.make_request(
                    method=method,
                    path=path,
                    headers=headers,
                    json=json
                )
            except requests.exceptions.SSLError as exc:
                print(exc)
                sleep(delay)

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
            fun=lambda response: response.json()['status'] == (
                'finished_with_success'
            ),
            timeout=timeout,
        ).json()

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
        ).json()

    def get_workers(self, headers=ADMIN_USER_HEADERS):
        return self.make_request(
            'GET',
            '/workers',
            headers=headers,
        ).json()

    def get_worker(self, worker_id, headers=ADMIN_USER_HEADERS):
        return self.make_request(
            'GET',
            '/workers/{worker_id}'.format(
                worker_id=worker_id
            ),
            headers=headers,
        ).json()
