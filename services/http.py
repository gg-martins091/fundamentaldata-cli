from services.log import log
from requests import Session, exceptions
from urllib.parse import urljoin
from services.utils import api_sleep

class Http(Session):
    def __init__(self, base_url=None):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        try:
            ret = super().request(method, joined_url, headers={'Authorization': 'Bearer '}, timeout=10, *args, **kwargs)
        except exceptions.Timeout:
            log.debug('timeout')
            ret = super().request(method, joined_url, headers={'Authorization': 'Bearer '}, *args, **kwargs)

        if ret.status_code == 429:
            api_sleep(True)
            ret = super().request(method, joined_url, headers={'Authorization': 'Bearer '}, *args, **kwargs)

        if ret.status_code == 429:
            api_sleep(True)
            ret = super().request(method, joined_url, headers={'Authorization': 'Bearer '}, *args, **kwargs)

        if ret.status_code == 429:
            raise Exception("rate limit")

        return ret


api = Http('https://api.dadosdemercado.com.br/v1/')
