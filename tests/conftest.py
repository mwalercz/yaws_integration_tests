from time import sleep

import docker
import pytest
import uuid

from tests.utils import auto_remove_network, auto_remove


@pytest.fixture
def client():
    return docker.from_env()


@pytest.yield_fixture
def network(client):
    with auto_remove_network(
            client.networks.create(
                name=str(uuid.uuid4()),
                driver='bridge'
            )
    ) as n:
        yield n


@pytest.yield_fixture
def postgres(client, network):
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
        network.connect(c, aliases=['postgres'])
        sleep(3)
        yield c


@pytest.yield_fixture
def broker(client, postgres, network):
    with auto_remove(
            create_broker(client, postgres, network)
    ) as c:
        sleep(2)
        yield c


@pytest.yield_fixture
def worker_1(client, network):
    with auto_remove(
            create_worker(client, network)
    ) as c:
        yield c


def create_worker(client, network):
    container = client.containers.run(
        'mwalercz/dq_worker',
        command='worker -c env.ini',
        environment={
            'BROKER_HOSTNAME': 'wss://broker:9000'
        },
        detach=True,
    )
    network.connect(container)
    return container


def create_broker(client, postgres, network):
    broker = client.containers.run(
        'mwalercz/dq_broker',
        command='broker -c env.ini',
        environment={
            'BROKER_DATABASE_HOSTNAME': 'postgres'
        },
        ports={'9001/tcp': ('127.0.0.1', 9001)},
        detach=True,
        hostname='broker',
    )
    network.connect(broker, aliases=['broker'])
    return broker
