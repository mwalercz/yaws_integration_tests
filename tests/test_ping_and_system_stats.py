from time import sleep


def test_ping_and_system_stats(
        broker, worker_1, broker_client
):
    sleep(2)
    workers = broker_client.get_workers()
    assert len(workers) == 1
