import ast
import hashlib
import time
import xml.etree.ElementTree as ET
from typing import Optional, Dict, TypedDict, Set, List
from urllib.parse import urlparse

import requests
import xmltodict


class ElementalException(Exception):
    """Base exception for all exceptions ElementalLive client could raise"""
    pass


class InvalidRequest(ElementalException):
    """Exception raised by 'request' with invalid request"""
    pass


class InvalidResponse(ElementalException):
    """Exception raised by 'request' with invalid response"""
    pass


EventIdDict = TypedDict('EventIdDict', {'id': str})

EventStatusDict = TypedDict('EventStatusDict', {'origin_url': str, 'backup_url': Optional[str], 'status': str})

DeviceAvailabilityDict = TypedDict('DeviceAvailabilityDict', {
    'id': str,
    'name': Optional[str],
    'device_name': str,
    'device_number': str,
    'device_type': str,
    'description': str,
    'channel': str,
    'channel_type': str,
    'quad': str,
    'availability': bool
})

PreviewUrlDict = TypedDict('PreviewUrlDict', {'preview_url': str})


class ElementalLive:
    def __init__(self, server_url: str, user: Optional[str] = None, api_key: Optional[str] = None,
                 timeout: Optional[int] = 5) -> None:
        self.server_url = server_url
        self.user = user
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def generate_headers(self, url: Optional[str] = "") -> Dict[str, str]:
        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            return {
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }
        else:
            expiration = int(time.time() + 120)
            parse = urlparse(url)
            prehash = "%s%s%s%s" % (
                parse.path, self.user, self.api_key, expiration)
            digest = hashlib.md5(prehash.encode('utf-8')).hexdigest()
            final_hash = "%s%s" % (self.api_key, digest)
            key = hashlib.md5(final_hash.encode('utf-8')).hexdigest()

            return {
                'X-Auth-User': self.user,
                'X-Auth-Expires': str(expiration),
                'X-Auth-Key': key,
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }

    def send_request(self, http_method: str, url: str, headers: Dict[str, str],
                     body: Optional[str] = "", timeout: Optional[int] = None) -> requests.Response:
        # Send request according to different methods
        try:
            timeout = timeout or self.timeout
            response = self.session.request(
                method=http_method, url=url, data=body, headers=headers, timeout=timeout)

        except requests.exceptions.RequestException as e:
            raise InvalidRequest(f"{http_method}: {url} failed\n{e}")
        if response.status_code not in (200, 201):
            raise InvalidResponse(
                f"{http_method}: {url} failed\nResponse: "
                f"{response.status_code}\n{response.text}")
        return response

    def create_event(self, event_xml: str, timeout: Optional[int] = None) -> EventIdDict:
        url = f'{self.server_url}/live_events'
        headers = self.generate_headers(url)
        response = self.send_request(
            http_method="POST", url=url, headers=headers, body=event_xml, timeout=timeout)
        xml_root = ET.fromstring(response.content)
        ids = xml_root.findall('id')
        event_id = str(ids[0].text)

        return {'id': event_id}

    def delete_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}'
        headers = self.generate_headers(url)
        self.send_request(http_method="DELETE", url=url, headers=headers, timeout=timeout)

    def start_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/start'
        body = "<start></start>"
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, body=body, timeout=timeout)

    def stop_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/stop'
        body = "<stop></stop>"
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, body=body, timeout=timeout)

    def reset_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/reset'
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, body="", timeout=timeout)

    def describe_event(self, event_id: str, timeout: Optional[int] = None) -> EventStatusDict:
        url = f'{self.server_url}/live_events/{event_id}'
        headers = self.generate_headers(url)
        response = self.send_request(http_method="GET", url=url,
                                     headers=headers, timeout=timeout)
        event_info = {}

        destinations = list(ET.fromstring(response.text).iter('destination'))
        event_info['origin_url'] = destinations[0].find('uri').text
        if len(destinations) > 1:
            event_info['backup_url'] = destinations[1].find('uri').text

        status = ET.fromstring(response.text).find('status')
        event_info['status'] = status.text

        return event_info

    def find_devices_in_use(self, timeout: Optional[int] = None) -> Set[str]:
        events_url = f'{self.server_url}/live_events?filter=active'
        events_headers = self.generate_headers(events_url)
        events = self.send_request(
            http_method="GET", url=events_url, headers=events_headers, timeout=timeout)
        events_list = ET.fromstring(events.text)

        # Find in use devices from active events
        in_use_devices = set()
        for device_name in events_list.iter('device_name'):
            in_use_devices.add(device_name.text)

        return in_use_devices

    def get_input_devices(self, timeout: Optional[int] = None) -> List[DeviceAvailabilityDict]:
        devices_url = f'{self.server_url}/devices'
        devices_headers = self.generate_headers(devices_url)
        devices = self.send_request(
            http_method="GET", url=devices_url, headers=devices_headers, timeout=timeout)
        devices_info = xmltodict.parse(devices.text)[
            'device_list']['device']

        devices_in_use = self.find_devices_in_use()

        for device in devices_info:
            device.pop('@href')
            device['availability'] = \
                (device['device_name'] not in devices_in_use)

        devices_info = sorted(
            devices_info, key=lambda d: int(d["id"]))
        return [dict(d) for d in devices_info]

    def get_input_device_by_id(self, input_device_id: str, timeout: Optional[int] = None) -> DeviceAvailabilityDict:
        devices_url = f'{self.server_url}/devices/{input_device_id}'
        devices_headers = self.generate_headers(devices_url)
        devices = self.send_request(
            http_method="GET", url=devices_url, headers=devices_headers, timeout=timeout)
        device_info = xmltodict.parse(devices.text)['device']
        devices_in_use = self.find_devices_in_use()
        device_info['availability'] = (device_info['device_name']
                                       not in devices_in_use)
        device_info.pop('@href')
        return dict(device_info)

    def generate_preview(self, input_id: str, timeout: Optional[int] = None) -> PreviewUrlDict:
        url = f'{self.server_url}/inputs/generate_preview'
        headers = self.generate_headers(url)

        headers['Accept'] = '*/*'
        headers['Content-Type'] = 'application/x-www-form-urlencoded; ' \
                                  'charset=UTF-8'

        # generate body
        data = f"input_key=0&live_event[inputs_attributes][0][source_type]=" \
               f"DeviceInput&live_event[inputs_attributes][0]" \
               f"[device_input_attributes][sdi_settings_attributes]" \
               f"[input_format]=Auto&live_event[inputs_attributes][0]" \
               f"[device_input_attributes][device_id]={input_id}"
        response = self.send_request(
            http_method="POST", url=url, headers=headers, body=data, timeout=timeout)

        response_parse = ast.literal_eval(response.text)

        if 'type' in response_parse and response_parse['type'] == 'error':
            raise ElementalException(
                f"Response: {response.status_code}\n{response.text}")
        else:
            preview_url = f'{self.server_url}/images/thumbs/' \
                          f'p_{response_parse["preview_image_id"]}_job_0.jpg'
            return {'preview_url': preview_url}

    def event_can_delete(self, channel_id: str, timeout: Optional[int] = None) -> bool:
        channel_info = self.describe_event(channel_id, timeout=timeout)
        return channel_info['status'] not in ('pending', 'running', 'preprocessing', 'postprocessing',)
