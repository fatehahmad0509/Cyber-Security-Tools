from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import json
import ssl
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI(title="Nova Web Secure API")

gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class WebsiteRequest(BaseModel):
    url: str


def check_ssl(hostname):
    try:
        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        return {
            "valid": "Yes",
            "issuer": dict(x[0] for x in cert["issuer"]).get(
                "organizationName", "Unknown"
            ),
            "expires": cert["notAfter"],
        }

    except Exception:
        return {
            "valid": "No",
            "issuer": "Unknown",
            "expires": "Unknown",
        }


def check_cookies(response):
    cookie = response.headers.get("Set-Cookie", "")

    return {
        "secure": "Yes" if "Secure" in cookie else "No",
        "httponly": "Yes" if "HttpOnly" in cookie else "No",
        "samesite": (
            "Lax"
            if "SameSite=Lax" in cookie
            else "Strict"
            if "SameSite=Strict" in cookie
            else "None"
            if "SameSite=None" in cookie
            else "Not specified"
        ),
    }


def analyze_with_ai(response, ssl_info, cookie_info):
    prompt = f"""
HTTPS Status: {response.url}
Status Code: {response.status_code}

Cookie Security:
Secure: {cookie_info["secure"]}
HttpOnly: {cookie_info["httponly"]}
SameSite: {cookie_info["samesite"]}

Server: {response.headers.get("Server")}
Strict-Transport-Security: {response.headers.get("Strict-Transport-Security")}
Content-Security-Policy: {response.headers.get("Content-Security-Policy")}
X-Frame-Options: {response.headers.get("X-Frame-Options")}
X-Content-Type-Options: {response.headers.get("X-Content-Type-Options")}
Permissions-Policy: {response.headers.get("Permissions-Policy")}

SSL Certificate:
Valid: {ssl_info["valid"]}
Issuer: {ssl_info["issuer"]}
Expiry Date: {ssl_info["expires"]}

Return JSON only.

{{
    "score":0,
    "risk":"",
    "summary":"",
    "strengths":[],
    "weaknesses":[],
    "recommendations":[],
    "reasoning":[]
}}
"""

    ai_response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )

    text = ai_response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


def analyze_url(url: str) -> dict:
    """Perform a security analysis for a URL.

    Can be called both by the FastAPI endpoint and directly (imported
    in-process, with no separate deployment). Uses synchronous I/O; async
    callers should wrap it with `asyncio.to_thread`.
    """
    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        raise RuntimeError(f"Could not reach the site: {e}") from e

    hostname = urlparse(url).hostname

    ssl_info = check_ssl(hostname)
    cookie_info = check_cookies(response)

    try:
        return analyze_with_ai(
            response=response,
            ssl_info=ssl_info,
            cookie_info=cookie_info,
        )
    except Exception as e:
        raise RuntimeError(f"AI Error: {e}") from e


@app.post("/analyze")
def analyze(data: WebsiteRequest):
    try:
        return analyze_url(data.url)
    except RuntimeError as e:
        detail = str(e)
        if detail.startswith("Could not reach the site"):
            raise HTTPException(status_code=400, detail=detail)
        raise HTTPException(status_code=500, detail=detail)
