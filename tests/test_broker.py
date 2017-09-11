def test_broker_is_responding(postgres, broker, broker_client):
    response = broker_client.make_request_with_retries(
        'GET',
        '/users/test/works',
    )
    assert response.status_code == 200
