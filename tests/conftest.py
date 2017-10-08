import uuid
from configparser import SafeConfigParser

import docker
import os
import pytest
import urllib3
from docker import APIClient

from definitions import ROOT_DIR
from utils.api import BrokerApiClient
from utils.auto_remove import auto_remove
from utils.containers_settings import BROKER_SETTINGS, POSTGRES_SETTINGS, WORKER_SETTINGS
from utils.health_checks import wait_for_postgres, wait_for_broker

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
def broker_client(broker_url):
    return BrokerApiClient(broker_url=broker_url)


@pytest.fixture(scope='session')
def remove_all_containers():
    cli = APIClient(base_url='unix://var/run/docker.sock')
    for container in cli.containers(all=True):
        cli.stop(container['Id'], timeout=2)
        cli.remove_container(container['Id'])


@pytest.fixture(scope='session')
def client(remove_all_containers):
    docker_client = docker.from_env()
    docker_client.networks.prune()
    docker_client.networks.create(
        name='docker_net',
        driver='bridge',
    )
    return docker_client


@pytest.yield_fixture(scope='session')
def postgres(client):
    with auto_remove(
            create_postgres(client)
    ) as c:
        wait_for_postgres(c)
        yield c


@pytest.yield_fixture
def broker(client, postgres):
    with auto_remove(
            create_broker(client)
    ) as c:
        wait_for_broker(c)
        yield c


@pytest.yield_fixture
def worker_1(client, broker):
    with auto_remove(
            create_worker(client)
    ) as c:
        yield c


def create_worker(client):
    return client.containers.run(**WORKER_SETTINGS)


def create_broker(client):
    return client.containers.run(**BROKER_SETTINGS)


def create_postgres(client):
    return client.containers.run(**POSTGRES_SETTINGS)
