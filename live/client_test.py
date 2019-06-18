from client import ElementalLive
import mock
import os
import re

USER = "FAKE"
API_KEY = "FAKE"


def mock_response(status=200, content="CONTENT",
                  json_data=None, raise_for_status=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()

    # mock raise_for_status call w/optional error
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status

    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content

    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp


def test_ElementalLive_should_receive_server_ip():
    e = ElementalLive('http://elemental.dev.cbsivideo.com/')
    assert e.server_ip == 'http://elemental.dev.cbsivideo.com/'


@mock.patch('requests.request')
def test_create_event_with_authentication(mock_request):
    """test create_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    mock_request.return_value = mock_response(
        status=201, content=response_from_elemental_api)

    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)
    event_id = client.create_event("live/templates/qvbr_mediastore.xml",
                                   {'username': os.getenv('ACCESS_KEY'),
                                    'password': os.getenv('SECRET_KEY'),
                                    'mediastore_container_master':
                                        'https://hu5n3jjiyi2jev.data.media'
                                        'store.us-east-1.amazonaws.com/master',
                                    'mediastore_container_backup':
                                        'https://hu5n3jjiyi2jev.data.medias'
                                        'tore.us-east-1.amazonaws.com/backup',
                                    'channel': "1", 'device_name': "0"})

    request_to_elemental = mock_request.call_args_list[0][1]
    assert request_to_elemental['url'] == 'http://elemental' \
                                          '.dev.cbsivideo.com/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
    assert event_id == "80"


@mock.patch('requests.request')
def test_create_event_without_authentication(mock_request):
    """test create_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    mock_request.return_value = mock_response(
        status=201, content=response_from_elemental_api)

    client = ElementalLive("http://elemental.dev.cbsivideo.com")
    event_id = client.create_event("live/templates/qvbr_mediastore.xml",
                                   {'username': os.getenv('ACCESS_KEY'),
                                    'password': os.getenv('SECRET_KEY'),
                                    'mediastore_container_master':
                                        'https://hu5n3jjiyi2jev.data.media'
                                        'store.us-east-1.amazonaws.com/master',
                                    'mediastore_container_backup':
                                        'https://hu5n3jjiyi2jev.data.medias'
                                        'tore.us-east-1.amazonaws.com/backup',
                                    'channel': "1", 'device_name': "0"})

    request_to_elemental = mock_request.call_args_list[0][1]
    assert request_to_elemental['url'] == 'http://elemental' \
                                          '.dev.cbsivideo.com/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
    assert event_id == "80"


@mock.patch('requests.request')
def test_delete_event_with_authentication(mock_request):
    """test delete_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_delete.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    # Mock delete function
    client.delete_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'DELETE'


@mock.patch('requests.request')
def test_delete_event_without_authentication(mock_request):
    """test delete_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_delete.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)')
    client = ElementalLive("http://elemental.dev.cbsivideo.com")

    # Mock delete function
    client.delete_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'DELETE'


@mock.patch('requests.request')
def test_start_event_with_authentication(mock_request):
    """test start_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/start')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    # Mock delete function
    client.start_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_start_event_without_authentication(mock_request):
    """test start_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/start')
    client = ElementalLive("http://elemental.dev.cbsivideo.com")

    # Mock delete function
    client.start_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_stop_event_with_authentication(mock_request):
    """test stop_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/stop')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    # Mock delete function
    client.stop_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_stop_event_without_authentication(mock_request):
    """test stop_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/stop')
    client = ElementalLive("http://elemental.dev.cbsivideo.com")

    # Mock delete function
    client.stop_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
