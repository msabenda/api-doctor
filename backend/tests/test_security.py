import pytest
from pydantic import AnyHttpUrl

from app.security import UnsafeTargetError, system_resolver, validate_target


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResolver:
    def __init__(self, *addresses: str, error: OSError | None = None) -> None:
        self.addresses = set(addresses)
        self.error = error
        self.calls: list[tuple[str, int]] = []

    async def __call__(self, host: str, port: int) -> set[str]:
        self.calls.append((host, port))
        if self.error:
            raise self.error
        return self.addresses


@pytest.mark.anyio
async def test_system_resolver_returns_addresses() -> None:
    addresses = await system_resolver("localhost", 80)

    assert addresses


@pytest.mark.anyio
async def test_accepts_public_dns_addresses() -> None:
    resolver = FakeResolver("93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946")

    target = await validate_target(AnyHttpUrl("https://example.com./v1"), resolver)

    assert tuple(str(address) for address in target.addresses) == (
        "2606:2800:220:1:248:1893:25c8:1946",
        "93.184.216.34",
    )
    assert resolver.calls == [("example.com", 443)]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1",
        "http://127.1",
        "http://[::1]",
        "http://[::ffff:127.0.0.1]",
        "http://10.0.0.1",
        "http://169.254.169.254/latest/meta-data",
        "http://0.0.0.0",
        "http://224.0.0.1",
        "http://localhost",
        "http://api.localhost",
        "http://2130706433",
        "http://0x7f000001",
    ],
)
async def test_rejects_direct_non_public_and_ambiguous_hosts(url: str) -> None:
    with pytest.raises(UnsafeTargetError):
        await validate_target(AnyHttpUrl(url), FakeResolver("93.184.216.34"))


@pytest.mark.anyio
@pytest.mark.parametrize(
    "addresses",
    [
        ("93.184.216.34", "127.0.0.1"),
        ("10.0.0.4",),
        ("169.254.169.254",),
        ("::1",),
        ("not-an-ip",),
        (),
    ],
)
async def test_rejects_dns_answers_unless_every_address_is_public(
    addresses: tuple[str, ...],
) -> None:
    with pytest.raises(UnsafeTargetError):
        await validate_target(AnyHttpUrl("https://example.com"), FakeResolver(*addresses))


@pytest.mark.anyio
async def test_returns_safe_error_for_dns_failure() -> None:
    with pytest.raises(UnsafeTargetError, match="could not be resolved"):
        await validate_target(
            AnyHttpUrl("https://missing.example"), FakeResolver(error=OSError("resolver detail"))
        )


@pytest.mark.anyio
async def test_uses_explicit_port() -> None:
    resolver = FakeResolver("93.184.216.34")

    await validate_target(AnyHttpUrl("http://example.com:8080"), resolver)

    assert resolver.calls == [("example.com", 8080)]
