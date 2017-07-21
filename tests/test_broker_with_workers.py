from tests.conftest import create_worker
from tests.api import make_request, get_work_after_it_finishes, post_work, get_user_works
from tests.utils import auto_remove_multiple


def test_spawn_broker_and_worker_post_work(broker, worker_1):
    work_id = post_work('ls')
    get_work_after_it_finishes(work_id)


def test_spawn_broker_worker_post_two_works(broker, worker_1):
    post_work('mkdir cool')
    work_id = post_work('ls')
    response = get_work_after_it_finishes(work_id)
    work = response.json()['work']
    assert 'cool' in work['events'][2]['context']['output']


def test_spawn_broker_three_workers_post_multiple_works(client, network, broker):
    with auto_remove_multiple([
        create_worker(client, network),
        create_worker(client, network),
        create_worker(client, network)
    ]) as workers_containers:
        number_of_works = 15
        work_ids = [post_work('ls') for i in range(0, number_of_works)]
        responses = [
            get_work_after_it_finishes(work_id)
            for work_id in work_ids]
        worker_ids = set(
            response.json()['work']['events'][2]['context']['worker_id']
            for response in responses
        )
        assert len(worker_ids) == 3

        print(b'BROKER' + broker.logs())
        print(get_user_works('test').json())
