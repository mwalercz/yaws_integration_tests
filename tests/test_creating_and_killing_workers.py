from time import sleep

from definitions import TEST_WORKS_DIR
from tests.api import post_work, get_user_work
from tests.conftest import create_worker
from tests.utils import auto_remove


def test_create_work_kill_worker_add_worker(client, broker):
    with auto_remove(create_worker(client, broker)):
        work_id = post_work(command='python 5_sec_loop.py', cwd=TEST_WORKS_DIR)

    with auto_remove(create_worker(client, broker)):
        sleep(7)

    work = get_user_work(work_id)
    assert work['status'] == 'finished_with_success'
    assert len(work['events']) > 3