# Security Notes

External source text is treated as untrusted data. The ingestion layer stores and normalizes content; it does
not execute instructions found in source text. HTML collection checks robots.txt and should only be used for
permitted public pages.

The local project is single-user and has no authentication or tenant isolation. Production deployment needs
authentication, authorization, tenant-scoped queries, HTTPS, secret management, rate limiting, audit logging,
and a managed database.

Real notification providers must be implemented behind explicit credentials and authorized recipient checks.
