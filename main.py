import typing

from subnet.keenetic import KeeneticApi
from subnet.ns_loock import NsResolverLoockup, DNSResolvers
from subnet.static_routes import StaticRouteTable, StaticRouteItem, StaticRoutes

DOMAINS_FILE = "subnet/domains.txt"
IP_ADDR_FILE = "subnet/ns_loockup.json"

STATIC_KEENETIC_CONFIG = {
    "auto": True,  # <-- AUTO USE CONFIG
    "gateway": "10.0.0.1",  # <-- IP ADDRESS CLIENT VPN
    "interface": "wg1",  # <-- NAME INTERFACE CLIENT VPN
}

api = KeeneticApi(
    login="...",
    password="...",
    ip_addr="192.168.100.1:280",  # <-- USE IP ADDRESSES
)

ns_resolver = NsResolverLoockup(
    resolvers={DNSResolvers.local, DNSResolvers.google, DNSResolvers.cloudflare},
    ns_verbose=False,
    ns_tcp=False,
)

manager = StaticRoutes(filename=IP_ADDR_FILE)


def domain_to_ip() -> None:
    with open(DOMAINS_FILE, "r") as fin:
        domains = [x.strip(" \n:,;") for x in fin.readlines()]
    domain_map = ns_resolver.resolve(domains=domains)
    tb = StaticRouteTable(
        table=[
            StaticRouteItem(domain=domain, ip_resolve=list(ip_resolve))
            for domain, ip_resolve in domain_map.items()
        ]
    )
    manager.save(tb=tb)


def keenetic_remove_route() -> None:
    routes = api.request(query="rci/ip/route")
    payload_keenetic: typing.List[typing.Dict[typing.Hashable, typing.Any]] = [
        {
            "ip": {
                "route": {
                    **route,
                    "no": True,
                }
            }
        }
        for route in routes
    ]
    payload_keenetic += [{"system": {"configuration": {"save": True}}}]
    api.request(query="rci/", json=payload_keenetic)


def keenetic_add_route() -> None:
    table = manager.get()
    routes = manager.generate_static_route(tb=table)
    payload_keenetic: typing.List[typing.Dict[typing.Hashable, typing.Any]] = [
        {
            "ip": {
                "route": {
                    **STATIC_KEENETIC_CONFIG,
                    "comment": route.domain,
                    "host": route.ip_addr,
                }
            }
        }
        for route in routes
    ]
    payload_keenetic += [{"system": {"configuration": {"save": True}}}]
    api.request(query="rci/", json=payload_keenetic)


if __name__ == "__main__":
    # Domain to ip addresses
    domain_to_ip()
    # Clear static routes keenetic
    keenetic_remove_route()
    # Add pre-complete static routes on keenetic
    keenetic_add_route()
