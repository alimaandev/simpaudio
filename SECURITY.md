# Security Policy

## Reporting a vulnerability

If you find a security issue in Simpaudio, please report it privately using
GitHub's **private vulnerability reporting** for this repository:

1. Go to **https://github.com/alimaandev/simpaudio/security/advisories**
2. Click **New draft security advisory**
3. Describe the issue, including how to reproduce it and what impact it has

Please do **not** open a public issue for security vulnerabilities.

You can expect an acknowledgement within a few days and a fix as soon as a
reproducible issue is understood.

## Scope

Simpaudio is an offline desktop application. It downloads voices, models and
updates over HTTPS, and stores user settings locally. Relevant areas for
security review include:

- Anything that downloads files from the internet (Piper voices, Kokoro and
  Whisper models)
- Handling of untrusted files (audio, text, EPUB, PDF imports)
- SSML parsing of user-supplied content

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.0   | Yes (current)      |
| < 1.0.0 | No                 |
