from time import sleep
from typing import NamedTuple
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth


class Credentials(NamedTuple):
    username: str
    password: str


class BrokerApiClient:
    TEST_USER_CREDENTIALS = Credentials(username='test', password='test')
    ADMIN_USER_CREDENTIALS = Credentials(username='admin', password='admin')

    def __init__(self, broker_url):
        self.broker_url = broker_url

    def make_request(self, method, path, credentials=None, json=None):
        url = urljoin(self.broker_url, path)
        credentials = credentials or self.TEST_USER_CREDENTIALS
        auth = HTTPBasicAuth(credentials.username, credentials.password)
        print(
            'Request to broker:\n'
            'url: {}\n'
            'credentials: {}\n'
            'method: {}\n'
            'json: {}'.format(
                url, credentials, method, json
            )
        )
        response = requests.request(
            method=method,
            url=url,
            auth=auth,
            verify=False,
            json=json
        )
        print(
            'Response from broker:\n'
            'status: {}\n'
            'text: {}\n'.format(response.status_code, response.text)
        )
        return response

    def make_request_with_retries(self, method, path, credentials=None, json=None, timeout=10, delay=1):
        for i in range(0, int(timeout / delay)):
            try:
                return self.make_request(
                    method=method,
                    path=path,
                    credentials=credentials,
                    json=json
                )
            except requests.exceptions.SSLError as exc:
                print(exc)
                sleep(delay)

    def make_request_until(
            self, method, path, fun, credentials=None,
            json=None, timeout=10, delay=1.0
    ):
        for i in range(0, int(timeout / delay)):
            response = self.make_request(method, path, credentials, json)
            if fun(response):
                return response
            sleep(delay)

        raise Exception('Timeout!')

    def get_user_work_with_status(
            self, work_id, user='test', timeout=5, status='FINISHED'
    ):
        return self.make_request_until(
            method='GET',
            path='/works/{work_id}'.format(
                user=user,
                work_id=work_id,
            ),
            fun=lambda response: response.json()['status'] == status,
            timeout=timeout,
        ).json()

    def post_user_work(self, command, cwd='/home/test', user='test'):
        response = self.make_request(
            'POST',
            '/works'.format(user=user),
            json={
                'command': command,
                'cwd': cwd,
                'env': {},
            }
        )
        assert response.status_code == 200
        return response.json()['work_id']

    def get_user_works(self, user='test'):
        return self.make_request(
            'GET',
            '/works'.format(user=user)
        )

    def get_user_work(self, work_id, user='test'):
        return self.make_request(
            'GET',
            '/works/{work_id}'.format(
                user=user,
                work_id=work_id
            )
        ).json()

    def get_workers(self, credentials=ADMIN_USER_CREDENTIALS):
        return self.make_request(
            'GET',
            '/workers',
            credentials=credentials,
        ).json()

    def get_worker(self, worker_id, credentials=ADMIN_USER_CREDENTIALS):
        return self.make_request(
            'GET',
            '/workers/{worker_id}'.format(
                worker_id=worker_id
            ),
            credentials=credentials,
        ).json()

    def post_user(self, username, is_admin=False, credentials=ADMIN_USER_CREDENTIALS):
        return self.make_request(
            'POST',
            '/users',
            credentials=credentials,
            json={
                'username': username,
                'is_admin': is_admin
            }
        ).json()
