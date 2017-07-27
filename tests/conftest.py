import uuid
from configparser import SafeConfigParser

import docker
import os
import pytest
from docker import APIClient

from definitions import ROOT_DIR
from utils.api import BrokerApiClient
from utils.auto_remove import auto_remove_network, auto_remove
from utils.containers_settings import BROKER_SETTINGS, POSTGRE_SETTINGS
from utils.health_checks import wait_for_postgres, wait_for_broker


def pytest_addoption(parser):
    parser.addoption(
        "--settings", action="store",
        default="develop.ini", help="config name"
    )


@pytest.fixture
def conf(request):
    conf_name = request.config.getoption("--settings")
    conf_path = os.path.join(ROOT_DIR, 'conf', conf_name)
    parser = SafeConfigParser(os.environ)
    parser.read(conf_path)
    return parser


@pytest.fixture
def broker_url(conf):
    return conf.get('broker', 'url')


@pytest.fixture
def ports_exposed(conf):
    return conf.getboolean('docker', 'ports_exposed')


@pytest.fixture
def broker_client(broker_url):
    return BrokerApiClient(broker_url=broker_url)


@pytest.fixture(scope='session')
def remove_all_containers():
    cli = APIClient(base_url='unix://var/run/docker.sock')
    for container in cli.containers():
        cli.stop(container['Id'], timeout=2)
        cli.remove_container(container['Id'])


@pytest.fixture
def client(remove_all_containers):
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
def postgres(client, network, ports_exposed):
    with auto_remove(
            create_postgres(client, ports_exposed)
    ) as c:
        network.connect(c, aliases=['postgres'])
        wait_for_postgres(c)
        yield c


@pytest.yield_fixture
def broker(client, postgres, network, ports_exposed):
    with auto_remove(
            create_broker(client, postgres, network, ports_exposed)
    ) as c:
        wait_for_broker(c)
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
            'BROKER_URL': 'wss://broker:9000'
        },
        detach=True,
    )
    network.connect(container)
    return container


def create_broker(client, postgres, network, ports_exposed):
    if ports_exposed:
        broker_settings = BROKER_SETTINGS.copy()
        broker_settings.update(dict(
            ports={'9001/tcp': ('127.0.0.1', 9001)}
        ))
    else:
        broker_settings = BROKER_SETTINGS
    broker = client.containers.run(**broker_settings)
    network.connect(broker, aliases=['broker'])
    return broker


def create_postgres(client, ports_exposed):
    if ports_exposed:
        postgre_settings = POSTGRE_SETTINGS.copy()
        postgre_settings.update(dict(
            ports={'5432/tcp': ('127.0.0.1', 5432)},
        ))
    else:
        postgre_settings = POSTGRE_SETTINGS

    return client.containers.run(**postgre_settings)
