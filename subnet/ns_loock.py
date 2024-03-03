import typing
from enum import Enum

from nslookup import Nslookup


class DNSResolvers(str, Enum):
    local = "local"
    google = "google"
    cloudflare = "cloudflare"


class NsResolverLoockup:
    def __init__(
        self,
        resolvers: set[DNSResolvers] | None = None,
        ns_verbose: bool = False,
        ns_tcp: bool = False,
    ):
        self.resolvers = resolvers or {DNSResolvers.local}
        self.ns_verbose = ns_verbose
        self.ns_tcp = ns_tcp

    def _init_resolver(self, resolver: DNSResolvers) -> Nslookup:
        template: dict[DNSResolvers, list[str]] = {
            DNSResolvers.local: [],
            DNSResolvers.google: ["8.8.8.8", "8.4.4.8"],
            DNSResolvers.cloudflare: ["1.1.1.1", "1.0.0.1"],
        }
        return Nslookup(
            dns_servers=template[resolver], verbose=self.ns_verbose, tcp=self.ns_tcp
        )

    def resolve(self, domains: list[str]) -> dict[str, set[str]]:
        result: typing.Dict[str, typing.Set[str]] = {
            domain: set() for domain in domains
        }
        for resolver in self.resolvers:
            dns_query = self._init_resolver(resolver=resolver)
            for domain in domains:
                ips_record = dns_query.dns_lookup(domain=domain)
                [result[domain].add(ip) for ip in ips_record.answer]
        return result
