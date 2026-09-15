# Security policy

## Reporting a vulnerability

Please do not disclose vulnerabilities publicly before a fix is available. Open a private GitHub security advisory for the repository owner and include reproduction steps, impact, and suggested remediation when possible.

## Security design

API Doctor treats URLs, headers, and request bodies as untrusted input. Future outbound request support must block non-HTTP protocols, private and special-purpose networks, unsafe redirects, DNS rebinding, oversized payloads, and secret leakage. TLS verification must remain enabled.

The MVP does not persist requests, credentials, or response history. Never commit `.env` files or credentials. Logs and errors must redact authentication headers and cookies.

## Supported versions

Only the latest commit on the default branch is supported during early development.
