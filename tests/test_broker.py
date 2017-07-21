from tests.api import make_request


def test_broker_is_responding(postgres, broker, network):
    response = make_request(
        'GET',
        '/users/test/works',
    )
    assert response.status_code == 200
