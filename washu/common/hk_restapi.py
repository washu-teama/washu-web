import requests
import json
import logging

from datetime import datetime, timedelta


class LoggingBase:
    def __init__(self):
        self.init()

    def init(self):
        self.log = logging.getLogger(str(self.__class__))
        self.log.setLevel(logging.DEBUG)

        streamHandler = logging.StreamHandler()

        self.log.addHandler(streamHandler)

    def debug(self, *args,  **kwargs):
        self.log.debug(*args, exc_info=1, **kwargs)

    def info(self, *args, **kwargs):
        self.log.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.log.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.log.critical(*args, **kwargs)


class SmartPlugBase(LoggingBase):
    OPEN_BASE = "https://open.hknetworks.kr/smartlife"
    API_BASE = "https://eco.hknetworks.kr/app"
    def __init__(self, client_id, client_secret, id=None, pwd=None):
        super(SmartPlugBase, self).__init__()

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.access_token_expire = None
        self.code = None
        if id and pwd:
            self.login(id, pwd)
            self.get_token()

    def _post(self, url, data_=None, json_=None, auth=True):
        self.log.debug("post to " + url)
        headers = {}
        if auth:
            headers = {
                "accessToken": self.access_token
            }
        response = requests.post(url, data=data_, json=json_, headers=headers)

        if response.status_code != 200:
            self.log.error("error when post to {}[{}]".format(url, response.status_code))
            pass  # TODO(choiking10) 예외 처리

        return json.loads(response.content.decode("utf-8"))

    def _post_open(self, to_php, data):
        return self._post("/".join([self.OPEN_BASE, to_php]),
                          data_=data, auth=False)

    def _post_api(self, to, data):
        return self._post("/".join([self.API_BASE, to]),
                          json_=data, auth=True)

    def login(self, id, pwd):
        data = {
            "clientid": self.client_id,
            "userid": id,
            "password": pwd
        }
        result = self._post_open("login_noui.php",data=data)
        self.log.debug(str(result))

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
        self.log.debug(str(result))

        self.access_token = result["access_token"]
        self.access_token_expire = datetime.now() +\
                                   timedelta(seconds=result["expires_in"])

    def token_refresh(self):
        if datetime.now() >= self.access_token_expire:
            self.token_refresh()

    def onoff(self, serial_number, state, port=0):
        data = {
            "protocol": 3,
            "sn": serial_number,
            "port": port,
            "state": state
        }
        result = self._post_api("sww/200", data)
        self.log.debug(result)

        if result["code"] != 200:
            self.log.error("on/off fail {}".format(result))

    def get_device_info(self, device="all"):
        data = {
            "protocol": 3,
            "dev": device
        }

        result = self._post_api("user/500", data)
        self.log.debug(result)

        return result["data"]["dev"]


def get_smartplug_api_client():
    from django.conf import settings
    config = settings.HK_NETWORKS_CONFIG
    plug = SmartPlugBase(client_id=config["client_id"],
                         client_secret=config["client_secret"],
                         id=config["id"],
                         pwd=config["password"])

    return plug
