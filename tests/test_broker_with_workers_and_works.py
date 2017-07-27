from tests.conftest import create_worker
from utils.auto_remove import auto_remove_multiple


def test_spawn_broker_and_worker_post_work(broker, worker_1, broker_client):
    work_id = broker_client.post_user_work('ls')
    broker_client.get_user_work_after_finish_with_success(work_id)


def test_spawn_broker_worker_post_two_works(
        broker, worker_1, broker_client
):
    broker_client.post_user_work('mkdir cool')
    work_id = broker_client.post_user_work('ls')
    response = broker_client.get_user_work_after_finish_with_success(work_id)
    work = response.json()['work']
    assert 'cool' in work['events'][2]['context']['output']


def test_spawn_broker_three_workers_post_multiple_works(
        client, network, broker, broker_client
):
    with auto_remove_multiple([
        create_worker(client, network),
        create_worker(client, network),
        create_worker(client, network)
    ]) as workers_containers:
        number_of_works = 15
        work_ids = [broker_client.post_user_work('ls') for i in range(0, number_of_works)]
        responses = [
            broker_client.get_user_work_after_finish_with_success(work_id)
            for work_id in work_ids
            ]
        worker_ids = set(
            response.json()['work']['events'][2]['context']['worker_id']
            for response in responses
        )
        assert len(worker_ids) == 3

        print(b'BROKER' + broker.logs())
        print(broker_client.get_user_works('test').json())
