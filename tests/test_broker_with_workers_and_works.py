from tests.conftest import create_worker
from utils.auto_remove import auto_remove_multiple


def test_spawn_broker_and_worker_post_work(broker, worker_1, broker_client):
    work_id = broker_client.post_user_work('ls')
    broker_client.get_user_work_with_status(work_id)


def test_spawn_broker_worker_post_two_works(
        broker, worker_1, broker_client
):
    mkdir_work_id = broker_client.post_user_work('mkdir cool')
    broker_client.get_user_work_with_status(mkdir_work_id)
    ls_work_id = broker_client.post_user_work('ls')
    ls_work = broker_client.get_user_work_with_status(ls_work_id)
    assert 'cool' in ls_work['events'][2]['context']['output']


def test_spawn_broker_three_workers_post_multiple_works(
        client, broker, broker_client
):
    with auto_remove_multiple([
        create_worker(client),
        create_worker(client),
        create_worker(client)
    ]) as workers_containers:
        number_of_works = 15
        work_ids = [broker_client.post_user_work('ls') for i in range(0, number_of_works)]
        finished_works = [
            broker_client.get_user_work_with_status(work_id, timeout=20)
            for work_id in work_ids
        ]
        worker_ids = set(
            finished_work['events'][2]['context']['worker_socket']
            for finished_work in finished_works
        )
        assert len(worker_ids) == 3


