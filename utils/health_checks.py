from time import sleep

from docker import APIClient
from docker.errors import APIError
from requests.exceptions import SSLError


def wait_for_postgres(container, timeout=20, delay=1):
    success_times = 0
    for i in range(0, int(timeout / delay)):
        response = container.exec_run(
            'pg_isready',
        )
        if response == b'/var/run/postgresql:5432 - accepting connections\n':
            success_times += 1
            if success_times == 2:
                return
        else:
            print(b'Waiting for postgres: ' + response)
            sleep(delay)

    raise Exception('Timeout. Postgres not responding.')


def wait_for_broker(container, timeout=20, delay=1):
    cli = APIClient(base_url='unix://var/run/docker.sock')
    for i in range(0, int(timeout / delay)):
        try:
            ex = cli.exec_create(container.id, cmd="bash -c 'curl --insecure https://`hostname`:9001/ping'")
            response = cli.exec_start(ex)
            if b'pong' in response:
                return
            else:
                print(b'Waiting for broker: ' + response)
                sleep(delay)
        except (APIError, SSLError) as exc:
            print(exc)
            sleep(delay)
    raise Exception('Timeout. Broker not responding.')