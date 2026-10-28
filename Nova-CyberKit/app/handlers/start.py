"""/start command."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="start")

WELCOME_TEXT = """\
👋 <b>Welcome to Nova CyberKit!</b>

This bot is a private OSINT toolkit built for your personal use.

<b>Available commands:</b>

🌐 <b>/ip</b> &lt;ip or domain&gt;
Country, region, city, ISP, ASN and location info for an IP/host.

🔒 <b>/website</b> &lt;url&gt;
Site security and technology analysis with Nova Web Secure and BuiltWith.

🕵️ <b>/username</b> &lt;username&gt;
Searches for the username across different platforms on whatsmyname.me.

📞 <b>/phone</b> &lt;number&gt;
Country, carrier, region and validity info (enter in international format, e.g. +905551234567).

🔎 <b>/search</b> &lt;query&gt;
Quick web search via DuckDuckGo.

🔐 <b>/hash</b> [md5|sha1|sha256|sha512|bcrypt|argon2] &lt;text&gt;
Computes hashes (default: all).

✅ <b>/verify</b> &lt;hash&gt; &lt;text&gt;
Compares text against a hash and detects its type.

🔑 <b>/password</b> [length]
Generates a cryptographically secure random password (default 16).

🔤 <b>/b64encode</b> (as a reply to a photo/file)
Converts a file to base64 text.

🔤 <b>/b64decode</b> &lt;base64&gt;
Converts base64 text to a file.

☠️ <b>/pwnedpassword</b> &lt;password&gt;
Checks whether a password appears in breaches using the Have I Been Pwned k-anonymity API.

📧 <b>/holehe</b> &lt;email&gt;
Scans which sites an email address is registered on.

📱 <b>/phoneinfo</b> &lt;number&gt;
Runs a PhoneInfoga OSINT scan on a phone number.

🛰️ <b>/nmap</b> &lt;ip or domain&gt;
Performs service (-sV) and operating system (-O) detection on the target. Only use on authorized targets.

🔗 <b>Quick links:</b>
/facecheck • /pimeyes • /geospy • /hive • /aiornot • /whatsmyname • /imginn

If you send a command without arguments, I will show you a usage example.
"""


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT)
