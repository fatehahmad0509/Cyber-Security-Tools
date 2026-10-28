"""Application-wide settings.

All values are read from the .env file. See .env.example
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Telegram ---
    bot_token: str

    # --- Database ---
    database_url: str

    # --- IP Lookup ---
    ipapi_base_url: str = "http://ip-api.com/json"

    # --- Nova Web Secure ---
    nova_web_secure_url: str = "http://localhost:8000/analyze"
    nova_web_secure_timeout: int = 30

    # --- BuiltWith ---
    builtwith_api_key: str = ""
    builtwith_base_url: str = "https://api.builtwith.com/v21/api.json"

    # --- Phone Lookup ---
    phone_lookup_api_key: str = ""
    phone_lookup_base_url: str = "https://api.veriphone.io/v2/verify"

    # --- Username Lookup ---
    username_lookup_concurrency: int = 60
    username_lookup_timeout: int = 15
    username_lookup_max_results: int = 40
    sherlock_timeout: int = 45

    # --- Pwned Passwords (HIBP k-anonymity, no key required) ---
    pwnedpasswords_base_url: str = "https://api.pwnedpasswords.com/range"

    # --- Holehe (email OSINT) ---
    holehe_timeout: int = 20

    # --- PhoneInfoga (phone OSINT, CLI installed on the system) ---
    phoneinfoga_binary: str = "phoneinfoga"
    phoneinfoga_timeout: int = 30

    # --- Nmap (default: -sT -sV, no raw socket required) ---
    nmap_binary: str = "nmap"
    nmap_timeout: int = 300
    # -O (OS detection) requires raw socket access; many PaaS providers such
    # as Render block it at the platform level. Only set this to True on a
    # server that allows raw socket access (e.g. your own VPS).
    nmap_os_detection: bool = False
    # With -O enabled, some servers may require root/sudo; see README.
    nmap_use_sudo: bool = False

    # --- General ---
    log_level: str = "INFO"
    request_timeout: int = 10


settings = Settings()
