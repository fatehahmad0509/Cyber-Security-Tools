# API Doc Finder

A lightweight, single-file Python tool that scans a target website for
commonly used API documentation endpoints — Swagger, OpenAPI, Redoc,
GraphQL playgrounds, and more.

## What it does

Many web applications expose their API documentation (or raw API schema)
at predictable paths, such as `/swagger.json`, `/docs`, `/openapi.json`,
or `/graphql`. This tool checks a target URL against a curated list of
100+ well-known documentation paths used by popular frameworks, including:

- Swagger / OpenAPI (general and framework-specific variants)
- Redoc
- FastAPI (`/docs`, `/redoc`, `/openapi.json`)
- Django REST Framework
- Spring Boot / Springfox (including Actuator endpoints)
- NestJS / Express
- GraphQL (GraphiQL, Playground, Voyager)
- RapiDoc, Stoplight, Postman collections
- AWS API Gateway / Apigee style paths

Any path that returns a non-error HTTP status is reported, along with its
content type and response size.

## Requirements

- Python 3.7+
- [`requests`](https://pypi.org/project/requests/)

```bash
pip install requests
```

## Usage

```bash
python api_doc_finder.py
```

The script will prompt you for a target URL:

```
Enter the target site URL (e.g. https://example.com): https://example.com
```

It will then scan each known path and print any that respond
successfully:

```
[*] Target: https://example.com/
[*] Paths to scan: 100

[+] 200 https://example.com/swagger.json (application/json, 4213 bytes)
[+] 200 https://example.com/docs (text/html, 1820 bytes)

[*] Scan complete. Found 2 possible documentation endpoint(s).

Summary:
  - https://example.com/docs [200]
  - https://example.com/swagger.json [200]
```

## Notes

- A fixed 3-second delay is used between requests to stay well under
  typical rate-limit thresholds (roughly 20 requests/minute) and to avoid
  putting unnecessary load on the target server.
- This is a simple, single-file tool with no external configuration —
  everything is handled through one input prompt.

## ⚠️ Responsible use

**Only scan systems you own or have explicit written permission to test.**
Running this tool against third-party systems without authorization may
violate their terms of service and, depending on jurisdiction, may be
illegal. This tool is intended for developers auditing their own APIs and
for authorized security testing (e.g., as part of a sanctioned
penetration test).

## License

MIT
