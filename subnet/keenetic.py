import typing

import requests
import hashlib


class KeeneticApi:
    def __init__(self, login: str, password: str, ip_addr: str):
        self._login = login
        self._password = password
        self._ip_addr = ip_addr
        self._auth_completed = False
        self._session = requests.session()

    def _auth_(self) -> bool:
        response = self._keen_request_(query="auth")
        if response.status_code == 401:
            md5 = (
                self._login
                + ":"
                + response.headers["X-NDM-Realm"]
                + ":"
                + self._password
            )
            md5 = hashlib.md5(md5.encode("utf-8"))
            sha = response.headers["X-NDM-Challenge"] + md5.hexdigest()
            sha = hashlib.sha256(sha.encode("utf-8"))
            response = self._keen_request_(
                query="auth", json={"login": self._login, "password": sha.hexdigest()}
            )
            if response.status_code == 200:
                return True
        elif response.status_code == 200:
            return True
        return False

    def _keen_request_(
        self,
        query: str,
        json: typing.Optional[
            typing.Union[
                typing.Dict[typing.Hashable, typing.Any], typing.List[typing.Any]
            ]
        ] = None,
    ) -> requests.Response:
        # конструируем url
        url = f"http://{self._ip_addr}/{query}"

        # если есть данные для запроса POST, делаем POST, иначе GET
        if json:
            return self._session.post(url, json=json)
        else:
            return self._session.get(url)

    def request(
        self,
        query: str,
        json: typing.Optional[
            typing.Union[
                typing.Dict[typing.Hashable, typing.Any], typing.List[typing.Any]
            ]
        ] = None,
    ) -> typing.Any:
        self._auth_()
        response = self._keen_request_(query=query, json=json)
        return response.json()
