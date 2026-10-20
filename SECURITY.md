# Security Policy

## Supported versions

Security fixes are provided for the latest release on the default branch.

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues. Use GitHub's private vulnerability reporting feature for this repository, or contact the maintainers through their GitHub profile. Include steps to reproduce and potential impact.

## Security design

- Provider credentials are read from environment variables and must never be committed.
- Search runs through the configured provider; the app does not fetch caller-supplied URLs.
- Retrieved source text is treated as untrusted input during synthesis.
- The browser UI writes generated content with safe DOM text APIs.
- SQLite stores queries, reports, and retrieved excerpts. Protect the database and volume if research may be sensitive.
- This project has no user authentication or per-user tenancy. Put it behind an authenticated gateway before exposing it to multiple users or the public internet.
