from time import sleep

from utils.commands import FIVE_SEC_LOOP
from utils.health_checks import wait_for_broker


def test_create_broker_dispatch_work_restart_broker(broker, worker_1, broker_client):
    work_id = broker_client.post_user_work(command=FIVE_SEC_LOOP)
    broker.stop(timeout=4)
    sleep(5)
    broker.start()
    wait_for_broker(broker)
    work = broker_client.get_user_work_with_status(
        work_id=work_id,
        timeout=15,
    )
    assert work['status'] == 'finished_with_success'


def test_create_broker_restart_broker(
        broker,
        broker_client
):
    work_id = broker_client.post_user_work(command=FIVE_SEC_LOOP)
    broker.stop(timeout=4)
    broker.start()
    wait_for_broker(broker)
    work = broker_client.get_user_work_with_status(
        work_id=work_id,
        timeout=15,
        status='unknown',
    )
    assert work['status'] == 'unknown'

