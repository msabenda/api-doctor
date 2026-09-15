import asyncio
import ipaddress
import socket
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pydantic import AnyHttpUrl

Resolver = Callable[[str, int], Awaitable[set[str]]]


class UnsafeTargetError(ValueError):
    """Raised when a URL may reach a non-public network destination."""


@dataclass(frozen=True)
class ValidatedTarget:
    url: AnyHttpUrl
    addresses: tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, ...]


async def system_resolver(host: str, port: int) -> set[str]:
    loop = asyncio.get_running_loop()
    records = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return {record[4][0] for record in records}


def _validate_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise UnsafeTargetError("target resolved to an invalid IP address") from error
    if (
        not address.is_global
        or address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        raise UnsafeTargetError("target resolves to a non-public IP address")
    return address


def _validate_hostname(host: str) -> None:
    normalized = host.rstrip(".").lower()
    if normalized == "localhost" or normalized.endswith(".localhost"):
        raise UnsafeTargetError("localhost targets are not allowed")


def _is_standard_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


async def validate_target(url: AnyHttpUrl, resolver: Resolver = system_resolver) -> ValidatedTarget:
    # Pydantic includes brackets in the serialized IPv6 host value.
    host = url.host.strip("[]")
    _validate_hostname(host)
    port = url.port or (443 if url.scheme == "https" else 80)

    if _is_standard_ip(host):
        raw_addresses = {host}
    else:
        try:
            raw_addresses = await resolver(host.rstrip("."), port)
        except OSError as error:
            raise UnsafeTargetError("target hostname could not be resolved") from error

    if not raw_addresses:
        raise UnsafeTargetError("target hostname did not resolve to an address")

    addresses = tuple(sorted((_validate_ip(value) for value in raw_addresses), key=str))
    return ValidatedTarget(url=url, addresses=addresses)
