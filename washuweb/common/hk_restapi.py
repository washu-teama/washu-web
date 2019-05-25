import requests
import json
import logging

from datetime import datetime, timedelta

log = logging.getLogger('django')


class HKBaseException(BaseException):
    code = 0


class HKNoResponseCodeException(HKBaseException):
    code = 600


class HKErrorException(HKBaseException):
    code = 400


class HKAccessTokenException(HKBaseException):
    code = 401


class HKDeviceOfflineException(HKBaseException):
    code = 500


class SmartPlugAPIClient:
    OPEN_BASE = "https://open.hknetworks.kr/smartlife"
    API_BASE = "https://eco.hknetworks.kr/app"

    def __init__(self, client_id, client_secret, id=None, pwd=None):
        super(SmartPlugAPIClient, self).__init__()

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.access_token_expired_at = None
        self.code = None
        if id and pwd:
            self.login(id, pwd)
            self.get_token()

    def _post(self, url, data_=None, json_=None, auth=True):
        log.debug("post to " + url)
        headers = {}
        if auth:
            headers = {
                "accessToken": self.access_token
            }
        response = requests.post(url, data=data_, json=json_, headers=headers)

        if response.status_code != 200:
            log.error("error when post to {}[{}]".format(url, response.status_code))
            pass  # TODO(choiking10) 예외 처리

        return json.loads(response.content.decode("utf-8"))

    def _post_open(self, to_php, data):
        return self._post("/".join([self.OPEN_BASE, to_php]),
                          data_=data, auth=False)

    def _post_api(self, to, data):
        api_result = self._post("/".join([self.API_BASE, to]), json_=data, auth=True)
        if len(api_result) == 0 or "code" not in api_result:
            raise HKNoResponseCodeException()
        if api_result["code"] != 200:
            for exception in HKBaseException.__class__.__subclasses__(HKBaseException):
                if exception.code == api_result["code"]:
                    raise exception(str(api_result))

        return api_result

    def login(self, id, pwd):
        data = {
            "clientid": self.client_id,
            "userid": id,
            "password": pwd
        }
        result = self._post_open("login_noui.php",data=data)
        log.debug(str(result))

        if result["ret"] != 0:
            pass  # TODO(choiking10) 예외 처리
        self.code = result["code"]

    def get_token(self):
        data = {
            "clientid": self.client_id,
            "clientsecret": self.client_secret,
            "code": self.code,
            "grant_type": "authorization_code"
        }
        result = self._post_open("refreshtoken.php",data=data)
        log.debug(str(result))

        self.access_token = result["access_token"]
        self.access_token_expired_at = datetime.now() + \
                                       timedelta(seconds=result["expires_in"])

    def set_token(self, access_token, access_token_expired_at):
        self.access_token = access_token
        self.access_token_expired_at = access_token_expired_at

    def onoff(self, serial_number, state, port=0):
        data = {
            "protocol": 3,
            "sn": serial_number,
            "port": port,
            "state": state
        }
        result = self._post_api("sww/200", data)
        log.debug(result)

        return result

    def get_device_info(self, device="all"):
        data = {
            "protocol": 3,
            "dev": device
        }

        result = self._post_api("user/500", data)
        log.debug(result)

        return result["data"]["dev"]

    def get_device_power(self, serial_numbers: list):
        data = {
            "protocol": 3,
            "sn": serial_numbers
        }

        result = self._post_api("sww/511", data)
        log.debug(result)

        return result["data"]


CLIENT = None


def get_smartplug_api_client():
    global CLIENT
    if CLIENT:
        return CLIENT

    from django.conf import settings
    config = settings.HK_NETWORKS_CONFIG
    CLIENT = SmartPlugAPIClient(client_id=config["client_id"],
                                client_secret=config["client_secret"],
                                id=config["id"],
                                pwd=config["password"])

    return CLIENT
