from time import sleep

import docker
import pytest

from tests.utils import auto_remove


@pytest.fixture
def client():
    return docker.from_env()


@pytest.yield_fixture
def postgres(client):
    with auto_remove(
            client.containers.run(
                'postgres:9.2-alpine',
                environment={
                    'POSTGRES_USER': 'dq_broker',
                    'POSTGRES_PASSWORD': 'dq_broker',
                    'POSTGRES_DB': 'dq_broker',
                },
                ports={'5432/tcp': ('127.0.0.1', 5432)},
                hostname='postgres',
                detach=True
            )
    ) as c:
        sleep(3)
        yield c


@pytest.yield_fixture
def broker(client, postgres):
    with auto_remove(
            create_broker(client, postgres)
    ) as c:
        sleep(2)
        yield c


@pytest.yield_fixture
def worker_1(client, broker):
    with auto_remove(
            create_worker(client, broker)
    ) as c:
        yield c


def create_worker(client, broker):
    return client.containers.run(
        'mwalercz/dq_worker',
        links=[(broker.name, 'broker')],
        hostname='worker',
        detach=True,
    )


def create_broker(client, postgres):
    return client.containers.run(
        'mwalercz/dq_broker',
        command='broker -c docker.ini',
        hostname='broker',
        ports={'9001/tcp': ('127.0.0.1', 9001)},
        links=[(postgres.name, 'postgres')],
        detach=True,
    )
