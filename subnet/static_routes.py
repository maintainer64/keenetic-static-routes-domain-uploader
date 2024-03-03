import json
import typing
from dataclasses import dataclass


@dataclass
class StaticRouteItem:
    domain: str
    ip_resolve: typing.List[str]

    @classmethod
    def from_dict(cls, value: typing.Dict[str, typing.Any]) -> "StaticRouteItem":
        return cls(
            domain=value.get("domain", ""), ip_resolve=value.get("ip_resolve", [])
        )

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {"domain": self.domain, "ip_resolve": self.ip_resolve}


@dataclass
class StaticRouteIp:
    domain: str
    ip_addr: str


@dataclass
class StaticRouteTable:
    table: typing.List[StaticRouteItem]

    @classmethod
    def from_dict(cls, value: typing.Dict[str, typing.Any]) -> "StaticRouteTable":
        return cls(
            table=[StaticRouteItem.from_dict(row) for row in value.get("table", [])]
        )

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "table": [x.to_dict() for x in self.table],
        }


class StaticRoutes:
    def __init__(self, filename: str):
        self._filename = filename

    def get(self) -> StaticRouteTable:
        with open(self._filename, "r") as fin:
            payload = json.load(fin)
        return StaticRouteTable.from_dict(value=payload)

    def save(self, tb: StaticRouteTable) -> None:
        with open(self._filename, "w") as fout:
            json.dump(tb.to_dict(), fout, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_static_route(tb: StaticRouteTable) -> list[StaticRouteIp]:
        ip_addr_set = set()
        result = []
        for row in tb.table:
            for ip_addr in row.ip_resolve:
                if ip_addr in ip_addr_set:
                    continue
                result.append(
                    StaticRouteIp(
                        domain=row.domain,
                        ip_addr=ip_addr,
                    )
                )
                ip_addr_set.add(ip_addr)
        return result
