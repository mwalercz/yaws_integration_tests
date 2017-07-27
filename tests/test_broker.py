def test_broker_is_responding(postgres, broker, network, broker_client):
    response = broker_client.make_request(
        'GET',
        '/users/test/works',
    )
    assert response.status_code == 200
