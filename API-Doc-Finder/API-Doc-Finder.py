#!/usr/bin/env python3
"""
api_doc_finder.py
------------------
Prompts for a target site URL and scans it for commonly used
API documentation endpoints (Swagger, OpenAPI, Redoc, etc.).

IMPORTANT: Only use this tool against systems you own or have
explicit permission to scan.

Usage:
    python api_doc_finder.py
    (you will be prompted to enter the target URL)
"""

import sys
import time
from urllib.parse import urljoin

# Delay between requests (seconds) - to avoid hitting rate limits
REQUEST_DELAY = 3

try:
    import requests
except ImportError:
    sys.exit("This tool requires the 'requests' library: pip install requests")


# Commonly used API documentation / schema endpoints
COMMON_DOC_PATHS = [
    # --- Swagger / OpenAPI (general) ---
    "swagger.json",
    "swagger.yaml",
    "swagger.yml",
    "swagger/",
    "swagger/index.html",
    "swagger-ui/",
    "swagger-ui.html",
    "swagger-ui/index.html",
    "swagger-resources",
    "swagger-resources/",
    "swagger-resources/configuration/ui",
    "swagger-resources/configuration/security",
    "api/swagger.json",
    "api/swagger.yaml",
    "api/swagger-ui.html",
    "api/v1/swagger.json",
    "api/v2/swagger.json",
    "api/v3/swagger.json",
    "v1/swagger.json",
    "v2/swagger.json",
    "v3/swagger.json",
    "v2/api-docs",
    "v3/api-docs",
    "v2/api-docs.json",
    "v3/api-docs.json",
    "api-docs",
    "api-docs/",
    "api-docs.json",
    "api/docs",
    "api/docs/",
    "api/api-docs",

    # --- OpenAPI (generic) ---
    "openapi.json",
    "openapi.yaml",
    "openapi.yml",
    "openapi/",
    "openapi",
    "api/openapi.json",
    "api/openapi.yaml",
    ".well-known/openapi.json",
    "spec.json",
    "spec.yaml",
    "schema.json",
    "schema.yaml",
    "schema/",
    "api/schema/",
    "api/schema.json",
    "api/schema.yaml",

    # --- Redoc ---
    "redoc",
    "redoc/",
    "redoc.html",
    "api/redoc",

    # --- FastAPI (default paths) ---
    "docs",
    "docs/",
    "redoc",
    "openapi.json",

    # --- Django REST Framework ---
    "api-auth/",
    "api/docs/",
    "api/schema/swagger-ui/",
    "api/schema/redoc/",

    # --- Spring Boot / Springfox ---
    "v2/api-docs",
    "swagger-ui.html",
    "actuator",
    "actuator/",
    "actuator/mappings",
    "actuator/health",
    "actuator/info",
    "actuator/env",

    # --- NestJS / Express common ---
    "api",
    "api/",
    "api/v1",
    "api/v1/",
    "api-json",
    "api-yaml",

    # --- GraphQL ---
    "graphql",
    "graphql/",
    "graphiql",
    "graphiql/",
    "playground",
    "playground/",
    "__schema",
    "voyager",

    # --- RapiDoc / Stoplight / Postman / other UI tools ---
    "rapidoc",
    "rapidoc/",
    "stoplight",
    "elements",
    "reference",
    "reference/",
    "api-reference",
    "api-reference/",
    "api-explorer",
    "api-explorer/",
    "explorer",
    "explorer/",
    "postman",
    "postman-collection.json",
    "postman_collection.json",

    # --- AWS API Gateway / Apigee style ---
    "swagger.json?format=openapi",
    "apidocs",
    "apidocs/",
    "apidoc",
    "apidoc/",

    # --- General / fallback ---
    "documentation",
    "documentation/",
    "developer",
    "developers",
    "developer/docs",
    "api-spec",
    "api-spec.json",
    ".well-known/ai-plugin.json",
]

# Remove duplicates while preserving order
_seen = set()
_deduped = []
for _p in COMMON_DOC_PATHS:
    if _p not in _seen:
        _seen.add(_p)
        _deduped.append(_p)
COMMON_DOC_PATHS = _deduped


def check_url(session: requests.Session, base_url: str, path: str):
    url = urljoin(base_url, path)
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code < 400:
            content_type = resp.headers.get("Content-Type", "")
            size = len(resp.content)
            return {
                "url": url,
                "status": resp.status_code,
                "content_type": content_type,
                "size": size,
            }
    except requests.RequestException:
        pass
    return None


def main():
    target = input("Enter the target site URL (e.g. https://example.com): ").strip()
    if not target.startswith("http://") and not target.startswith("https://"):
        target = "https://" + target
    base_url = target if target.endswith("/") else target + "/"

    session = requests.Session()

    print(f"\n[*] Target: {base_url}")
    print(f"[*] Paths to scan: {len(COMMON_DOC_PATHS)}\n")

    found = []
    for path in COMMON_DOC_PATHS:
        result = check_url(session, base_url, path)
        if result:
            found.append(result)
            print(
                f"[+] {result['status']} {result['url']} "
                f"({result['content_type']}, {result['size']} bytes)"
            )
        time.sleep(REQUEST_DELAY)

    print(f"\n[*] Scan complete. Found {len(found)} possible documentation endpoint(s).")
    if found:
        print("\nSummary:")
        for r in sorted(found, key=lambda x: x["url"]):
            print(f"  - {r['url']} [{r['status']}]")
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
