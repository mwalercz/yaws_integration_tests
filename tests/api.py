import socket
from time import sleep

import requests


def wait_for(address, port, timeout=5, delay=0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(0, int(timeout / delay)):
        try:
            s.connect((address, port))
            return
        except socket.error as e:
            print(e.errno)
            print(e.strerror)
            sleep(delay)
        finally:
            s.close()

    raise Exception('Cannot connect')


def make_request(method, path, headers=None, json=None):
    url = 'https://127.0.0.1:9001{path}'.format(path=path)
    headers = headers or {'username': 'test', 'password': 'test'}

    return requests.request(
        method=method,
        url=url,
        headers=headers,
        verify=False,
        json=json
    )


def make_request_until(
        method, path, fun, headers=None,
        json=None, timeout=5, delay=0.5
):
    for i in range(0, int(timeout / delay)):
        response = make_request(method, path, headers, json)
        if fun(response):
            return response
        sleep(delay)

    raise Exception('Timeout!')


def get_work_after_it_finishes(work_id, timeout=5):
    return make_request_until(
        method='GET',
        path='/users/test/works/{work_id}'.format(work_id=work_id),
        fun=lambda response: response.json()['work']['status'] == (
            'finished_with_success'
        ),
        timeout=timeout,
    )


def post_work(command, cwd='/home/test'):
    response = make_request(
        'POST',
        '/users/test/works',
        json={
            'command': command,
            'cwd': cwd,
            'env': {},
        }
    )
    assert response.status_code == 202
    return response.json()['work_id']


def get_user_works(user='test'):
    return make_request(
        'GET',
        '/users/{user}/works'.format(user=user)
    )


def get_user_work(work_id, user='test'):
    return make_request(
        'GET',
        '/users/{user}/works/{work_id}'.format(
            user=user,
            work_id=work_id
        )
    ).json()['work']
