from time import sleep

from tests.conftest import create_worker
from utils.auto_remove import auto_remove
from utils.commands import FIVE_SEC_LOOP


def test_create_work_kill_worker_add_worker(client, broker, broker_client):

    with auto_remove(create_worker(client)):
        work_id = broker_client.post_user_work(command=FIVE_SEC_LOOP, cwd='/home/test')
        sleep(1)

    with auto_remove(create_worker(client)):
        work = broker_client.get_user_work_with_status(
            work_id,
            timeout=10,
        )
        assert work['status'] == 'FINISHED'
        assert len(work['events']) > 3