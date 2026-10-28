# Nova CyberKit

A private, single-user, English-language Telegram OSINT bot.

## Architecture

```text
nova_cyberkit/
├── app/
│   ├── handlers/          # Telegram command handlers (aiogram Routers)
│   ├── services/          # Business logic that talks to external services
│   │   ├── ip_lookup.py         -> ip-api.com
│   │   ├── website_lookup.py    -> Nova Web Secure + BuiltWith combiner
│   │   ├── nova_web_secure.py   -> HTTP client for the Nova Web Secure microservice
│   │   ├── username_lookup.py   -> redirect to whatsmyname.me
│   │   ├── phone_lookup.py      -> numverify/apilayer-compatible phone lookup
│   │   ├── duckduckgo.py        -> duckduckgo-search (ddgs)
│   │   ├── pwned_service.py     -> Have I Been Pwned k-anonymity API
│   │   ├── holehe_service.py    -> holehe (email OSINT, used as a library)
│   │   ├── phoneinfoga_service.py -> phoneinfoga CLI (phone OSINT)
│   │   └── nmap_service.py      -> nmap CLI (port + service detection; -O optional)
│   ├── database/           # Async SQLAlchemy engine + CRUD
│   ├── models/             # whitelist table
│   ├── middlewares/        # WhitelistMiddleware (silently ignores unauthorized users)
│   ├── utils/              # logger, subprocess_tools (ANSI stripping + subprocess runner), long_output (sending long output), etc.
│   ├── config.py           # reads .env via pydantic-settings
│   └── bot.py              # Dispatcher / router setup
├── nova_web_secure_service/ # Nova Web Secure (in-process, no separate deployment needed)
├── scripts/manage_whitelist.py  # CLI for managing the whitelist
├── main.py
└── requirements.txt
```

## Installation

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the `.env` file (see the "Environment Variables" section below).

Create the database in PostgreSQL:

```sql
CREATE DATABASE nova_cyberkit;
```

The tables are created automatically the first time the bot runs (`init_db`).

### Nmap Setup

The `/nmap` command uses the `nmap` binary installed on the system:

```bash
sudo apt-get install -y nmap
```

By default, `nmap -Pn -sT -sV <target>` is run. `-sT` (TCP connect scan)
**does not require a raw socket**, so it works without problems on
containerized/sandboxed PaaS environments such as Render, Railway and
Fly.io.

`-O` (OS detection) requires raw socket access. Many PaaS providers,
Render included, block this entirely at the platform level (this is what the
`Couldn't open a raw socket. Error: Operation not permitted` error means) —
this is independent of the container's user privileges; `setcap` or `sudo`
will not help in this case. Only if you are running on a server that allows
raw socket access (such as your own VPS) can you enable `-O` by setting the
following in `.env`:

```
NMAP_OS_DETECTION=true
```

If you do not want to run the bot as root on such a server, you can instead
define a restricted NOPASSWD sudo rule for `nmap` only and set
`NMAP_USE_SUDO=true`:

```bash
# /etc/sudoers.d/nova-cyberkit-nmap
botuser ALL=(root) NOPASSWD: /usr/bin/nmap -Pn -sT -sV -O *
```

### PhoneInfoga Setup

The `/phoneinfo` command uses the `phoneinfoga` (Go) CLI installed on the
system:

```bash
go install github.com/sundowndev/phoneinfoga/v2/cmd/phoneinfoga@latest
```

The installed binary usually ends up under `$HOME/go/bin`; add this folder
to your PATH or set the `PHONEINFOGA_BINARY` variable in `.env` to the full
path of the binary.

## Add Yourself to the Whitelist

The bot does **not** reply to any user who is not on the whitelist (the
message is completely ignored). For this reason, you need to add your own
Telegram ID before running the bot for the first time (you can find your ID
with a bot such as @userinfobot):

```bash
python -m scripts.manage_whitelist add 123456789 "My Name"
python -m scripts.manage_whitelist list
```

## Nova Web Secure (no separate deployment needed anymore!)

For the `/website` command, the Nova Web Secure analysis runs in the same
process by default -- you do not need to deploy a separate service. You only
need to set `GEMINI_API_KEY` in the `.env` file.

Advanced: those who want to run the service on a separate machine can enable
the HTTP path by explicitly setting `NOVA_WEB_SECURE_URL` to a different
address:

```bash
# service side:
cd nova_web_secure_service; uvicorn Nova_Web_Secure:app --host 0.0.0.0 --port 8000

# in .env:
NOVA_WEB_SECURE_URL=http://1.2.3.4:8000/analyze
```

## Run the Bot

```bash
python main.py
```

## Environment Variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token obtained from BotFather |
| `DATABASE_URL` | Async PostgreSQL connection URL (`postgresql+asyncpg://...`) |
| `NOVA_WEB_SECURE_URL` | The `/analyze` address of your Nova Web Secure service |
| `BUILTWITH_API_KEY` | (optional) if empty, the BuiltWith step is skipped |
| `PHONE_LOOKUP_API_KEY` | numverify/apilayer free plan key |
| `USERNAME_LOOKUP_CONCURRENCY` | Number of concurrent requests in the WhatsMyName scan |
| `HOLEHE_TIMEOUT` | (optional) Holehe request timeout in seconds (default 20) |
| `PHONEINFOGA_BINARY` | (optional) path to the `phoneinfoga` binary (default: `phoneinfoga` from PATH) |
| `PHONEINFOGA_TIMEOUT` | (optional) PhoneInfoga timeout in seconds (default 30) |
| `NMAP_BINARY` | (optional) path to the `nmap` binary (default: `nmap` from PATH) |
| `NMAP_TIMEOUT` | (optional) Nmap timeout in seconds (default 300) |
| `NMAP_OS_DETECTION` | (optional) if `true`, `-O` is added; only meaningful on servers that allow raw socket access (default false, does not work on PaaS such as Render) |
| `NMAP_USE_SUDO` | (optional) if `true`, the `nmap` command is run with `sudo -n` (default false) |

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and command list |
| `/ip <ip\|domain>` | Location/ISP info via ip-api.com |
| `/website <url>` | Nova Web Secure + BuiltWith analysis |
| `/username <username>` | Redirects to whatsmyname.me |
| `/phone <+90...>` | Country, carrier, region, validity |
| `/search <query>` | DuckDuckGo search results |
| `/pwnedpassword <password>` | Password breach check via the Have I Been Pwned k-anonymity API |
| `/holehe <email>` | Scans the sites an email is registered on |
| `/phoneinfo <number>` | OSINT scan of a phone number with PhoneInfoga |
| `/nmap <ip\|domain>` | Port + service detection with `nmap -Pn -sT -sV` (`-O` optional, see `NMAP_OS_DETECTION`) |
| `/facecheck`, `/pimeyes`, `/geospy`, `/hive`, `/aiornot` | Sends the official website of the respective service |

## Notes / Limitations

- `/username`: Sherlock runs the `sherlock` command installed on the system
  as a subprocess; it is installed automatically via `requirements.txt`.
  For WhatsMyName, a 719-site dataset ships with the package under
  `app/services/data/wmn-data.json`; scan duration/aggressiveness can be
  tuned with `USERNAME_LOOKUP_CONCURRENCY` and `USERNAME_LOOKUP_TIMEOUT`.
- `/phone`: Since there is no completely keyless and reliable free service,
  a numverify/apilayer-compatible API is used; a key for the free plan can
  be obtained from numverify.com.
- `/facecheck`, `/pimeyes`, `/geospy`, `/hive`: The general terms of use and
  privacy/consent requirements of these services belong to their own
  platforms; the bot only redirects to the respective official site for
  these commands and does not send any automated queries.
- `/pwnedpassword`: No key is required; thanks to the k-anonymity model,
  only the first 5 characters of the password's SHA-1 hash are sent to HIBP,
  and the plain-text password is never logged or sent out.
- `/holehe`: The `holehe` package is installed automatically via
  `requirements.txt`; no additional setup is required. The query works by
  sending requests to the account/password-recovery endpoints of dozens of
  sites using the given email, so it may take a while.
- `/phoneinfo`: The `phoneinfoga` (Go) CLI must be installed on the system
  and available in PATH (see "PhoneInfoga Setup"). Scanners that are not
  configured (those requiring an API key, such as numverify) are skipped
  automatically.
- `/nmap`: `nmap` must be installed on the system (see "Nmap Setup"). The
  default mode (`-Pn -sT -sV`) does not require a raw socket (host discovery
  included, which is why `-Pn` is there) and works on PaaS environments,
  Render included. `-O` OS detection is optional (`NMAP_OS_DETECTION=true`)
  and is only meaningful on servers that allow raw socket access (such as a
  VPS); if needed it can be used together with `NMAP_USE_SUDO=true`. This
  command should only be used on systems you are **authorized to scan**;
  scanning third-party systems without permission may be illegal in many
  countries.
