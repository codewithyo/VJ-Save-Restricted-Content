# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import random
import re
import string
import time

import requests
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import Message

from config import API_HASH, API_ID
from database.db import db

SESSION_STRING_SIZE = 351


async def ensure_user_record(message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)


def random_word(length=8):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def normalize_phone_number(phone):
    phone = phone.strip().replace(" ", "")
    if not phone.startswith("+"):
        return "+" + phone
    return phone


class TelegramApiGenerator:
    """Small wrapper around my.telegram.org app creation/get flow."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    )

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://my.telegram.org",
                "Referer": "https://my.telegram.org/auth",
            }
        )
        self.random_hash = None

    def send_password(self, phone_number):
        response = self.session.post(
            "https://my.telegram.org/auth/send_password",
            data={"phone": phone_number},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if "random_hash" not in data:
            raise ValueError(data.get("error", "Unable to get random hash"))
        self.random_hash = data["random_hash"]
        return self.random_hash

    def auth_login(self, phone_number, code):
        if not self.random_hash:
            raise ValueError("random_hash not found, send_password first")

        response = self.session.post(
            "https://my.telegram.org/auth/login",
            data={
                "phone": phone_number,
                "random_hash": self.random_hash,
                "password": code,
            },
            timeout=30,
        )
        response.raise_for_status()

        if "stel_token" not in self.session.cookies:
            raise ValueError("Login failed or OTP invalid")

        return True

    @staticmethod
    def _extract_api_from_apps_page(page_text):
        # Primary parser from legacy HTML blocks.
        api = re.findall(
            r'<span class="form-control input-xlarge uneditable-input">\s*([^<\s]+)\s*</span>',
            page_text,
            flags=re.IGNORECASE,
        )
        if len(api) >= 2 and api[0].isdigit() and re.fullmatch(r"[0-9a-fA-F]{32}", api[1]):
            return int(api[0]), api[1]

        patterns = [
            (r'name="api_id"[^>]*value="(\d+)"', r'name="api_hash"[^>]*value="([0-9a-fA-F]{32})"'),
            (r'id="api_id"[^>]*value="(\d+)"', r'id="api_hash"[^>]*value="([0-9a-fA-F]{32})"'),
            (r'api_id[^0-9]{0,40}(\d{5,10})', r'api_hash[^0-9a-fA-F]{0,40}([0-9a-fA-F]{32})'),
        ]
        for id_pattern, hash_pattern in patterns:
            id_match = re.search(id_pattern, page_text, re.IGNORECASE | re.DOTALL)
            hash_match = re.search(hash_pattern, page_text, re.IGNORECASE | re.DOTALL)
            if id_match and hash_match:
                return int(id_match.group(1)), hash_match.group(1)

        # Last resort: extract the first plausible API pair from the page body.
        id_candidates = [int(x) for x in re.findall(r"\b(\d{5,10})\b", page_text)]
        hash_candidates = re.findall(r"\b([0-9a-fA-F]{32})\b", page_text)
        if id_candidates and hash_candidates:
            return id_candidates[0], hash_candidates[0]

        return None

    @staticmethod
    def _extract_create_hash(page_text):
        match = re.search(r'name="hash"\s+value="([^"]+)"', page_text)
        if match:
            return match.group(1)
        return None

    def get_or_create_app(self, app_title, app_shortname, app_desc):
        apps_page = self.session.get("https://my.telegram.org/apps", timeout=30)
        apps_page.raise_for_status()

        existing = self._extract_api_from_apps_page(apps_page.text)
        if existing:
            return existing

        form_hash = self._extract_create_hash(apps_page.text)
        if not form_hash:
            raise ValueError("Cannot find app form hash from my.telegram.org/apps")

        create_resp = self.session.post(
            "https://my.telegram.org/apps/create",
            data={
                "hash": form_hash,
                "app_title": app_title,
                "app_shortname": app_shortname,
                "app_url": "",
                "app_platform": "android",
                "app_desc": app_desc,
            },
            timeout=30,
        )
        create_resp.raise_for_status()

        if re.search(r"(APP_SHORTNAME_INVALID|APP_TITLE_INVALID|SHORTNAME|invalid|error)", create_resp.text, re.IGNORECASE):
            raise ValueError("Telegram rejected the app creation request. Try a different app name and shortname.")

        for _ in range(4):
            check_page = self.session.get("https://my.telegram.org/apps", timeout=30)
            check_page.raise_for_status()
            created = self._extract_api_from_apps_page(check_page.text)
            if created:
                return created
            time.sleep(1)

        fallback = self._extract_api_from_apps_page(create_resp.text)
        if fallback:
            return fallback

        raise ValueError("API ID/HASH not found after app creation. Telegram may not have created the app yet.")


@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    await ensure_user_record(message)
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        return
    await db.set_session(message.from_user.id, session=None)
    await message.reply("**Logout Successfully** ♦")


@Client.on_message(filters.private & ~filters.forwarded & filters.command(["generate"]))
async def generate_api(bot: Client, message: Message):
    await ensure_user_record(message)
    user_id = int(message.from_user.id)
    await message.reply(
        "<b>Telegram API Generator</b>\n\n"
        "Send your phone number with country code.\n"
        "Example: <code>+14155550123</code>\n\n"
        "Send /cancel to stop."
    )

    phone_msg = await bot.ask(user_id, "<b>Phone Number:</b>", filters=filters.text)
    if phone_msg.text.strip().lower() == "/cancel":
        return await phone_msg.reply("<b>Process cancelled.</b>")

    phone_number = normalize_phone_number(phone_msg.text)
    generator = TelegramApiGenerator()

    wait_msg = await bot.send_message(user_id, "Generating request token...")
    try:
        await asyncio.to_thread(generator.send_password, phone_number)
    except Exception as e:
        return await wait_msg.edit(
            f"<b>Failed to start generation.</b>\n<code>{e}</code>\n\n"
            "Check phone number format or try again later."
        )

    otp_msg = await bot.ask(
        user_id,
        "Enter the code received on Telegram for my.telegram.org login.\n"
        "Send it exactly as received. Spaces are removed automatically.\n\n"
        "Send /cancel to stop.",
        filters=filters.text,
        timeout=600,
    )
    if otp_msg.text.strip().lower() == "/cancel":
        return await otp_msg.reply("<b>Process cancelled.</b>")

    otp = otp_msg.text.strip().replace(" ", "")
    try:
        await asyncio.to_thread(generator.auth_login, phone_number, otp)
    except Exception as e:
        return await wait_msg.edit(f"<b>Login failed:</b> <code>{e}</code>")

    await wait_msg.edit("Fetching API ID and API HASH...")
    app_suffix = random_word(6)
    app_title = f"HRSaveRestricted {app_suffix}"
    app_shortname = f"hrsr{app_suffix}"
    app_desc = "HR save restricted account protection"

    try:
        api_id, api_hash = await asyncio.to_thread(
            generator.get_or_create_app,
            app_title,
            app_shortname,
            app_desc,
        )
    except Exception as e:
        return await wait_msg.edit(f"<b>API generation failed:</b> <code>{e}</code>")

    await db.set_api_id(user_id, api_id=api_id)
    await db.set_api_hash(user_id, api_hash=api_hash)

    await wait_msg.edit(
        "<b>API Generated Successfully</b>\n\n"
        f"<b>API ID:</b> <code>{api_id}</code>\n"
        f"<b>API HASH:</b> <code>{api_hash}</code>\n\n"
        "Saved to your account. Now run /login and send /skip on API prompt to use these values."
    )


@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    await ensure_user_record(message)
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**Your Are Already Logged In. First /logout Your Old Session. Then Do Login.**")
        return

    user_id = int(message.from_user.id)
    await message.reply(
        "**How To Create API ID And API HASH**\n\n"
        "Use /generate for automatic secure generation (recommended).\n"
        "Or send your own API ID manually below."
    )

    api_id_msg = await bot.ask(
        user_id,
        "<b>Send Your API ID.\n\n"
        "Click /skip to use saved/generated API values.\n"
        "NOTE: Using your own API is better for account protection.</b>",
        filters=filters.text,
    )

    if api_id_msg.text.strip().lower() == "/skip":
        api_id = await db.get_api_id(user_id)
        api_hash = await db.get_api_hash(user_id)
        if not api_id or not api_hash:
            if API_ID and API_HASH:
                api_id = API_ID
                api_hash = API_HASH
            else:
                return await api_id_msg.reply(
                    "**No saved API credentials found. Run /generate first, or send manual API ID and API HASH.**"
                )
    else:
        try:
            api_id = int(api_id_msg.text.strip())
        except ValueError:
            return await api_id_msg.reply("**API ID must be an integer, start again with /login**")

        api_hash_msg = await bot.ask(user_id, "**Now Send Me Your API HASH**", filters=filters.text)
        api_hash = api_hash_msg.text.strip()
        if not re.fullmatch(r"[0-9a-fA-F]{32}", api_hash):
            return await api_hash_msg.reply("**Invalid API HASH format, start again with /login**")

    phone_number_msg = await bot.ask(
        chat_id=user_id,
        text="<b>Please send your phone number including country code</b>\n"
        "<b>Example:</b> <code>+13124562345, +9171828181889</code>",
    )
    if phone_number_msg.text.strip().lower() == "/cancel":
        return await phone_number_msg.reply("<b>Process cancelled!</b>")

    phone_number = normalize_phone_number(phone_number_msg.text)
    client = Client(":memory:", api_id, api_hash)

    try:
        await client.connect()
    except ApiIdInvalid:
        return await phone_number_msg.reply("**API ID/API HASH is invalid. Generate again using /generate.**")
    except Exception as e:
        return await phone_number_msg.reply(f"**Failed to initialize login client:** <code>{e}</code>")

    await phone_number_msg.reply("Sending OTP...")
    try:
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await client.disconnect()
        return await phone_number_msg.reply("`PHONE_NUMBER` **is invalid.**")
    except Exception as e:
        await client.disconnect()
        return await phone_number_msg.reply(f"**Failed to send OTP:** <code>{e}</code>")

    phone_code_msg = await bot.ask(
        user_id,
        "Please check OTP in official Telegram app.\n\n"
        "If OTP is <code>12345</code>, send as <code>1 2 3 4 5</code>.\n\n"
        "Enter /cancel to cancel process.",
        filters=filters.text,
        timeout=600,
    )
    if phone_code_msg.text.strip().lower() == "/cancel":
        await client.disconnect()
        return await phone_code_msg.reply("<b>Process cancelled!</b>")

    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await client.disconnect()
        return await phone_code_msg.reply("**OTP is invalid.**")
    except PhoneCodeExpired:
        await client.disconnect()
        return await phone_code_msg.reply("**OTP is expired.**")
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(
            user_id,
            "**Two-step verification is enabled. Please send your password.\n\n"
            "Enter /cancel to cancel process.**",
            filters=filters.text,
            timeout=300,
        )
        if two_step_msg.text.strip().lower() == "/cancel":
            await client.disconnect()
            return await two_step_msg.reply("<b>Process cancelled!</b>")
        try:
            await client.check_password(password=two_step_msg.text)
        except PasswordHashInvalid:
            await client.disconnect()
            return await two_step_msg.reply("**Invalid Password Provided**")

    string_session = await client.export_session_string()
    await client.disconnect()

    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply("<b>Invalid session string generated</b>")

    try:
        user_data = await db.get_session(user_id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=api_id, api_hash=api_hash)
            await uclient.connect()
            await db.set_session(user_id, session=string_session)
            await db.set_api_id(user_id, api_id=api_id)
            await db.set_api_hash(user_id, api_hash=api_hash)
            try:
                await uclient.disconnect()
            except:
                pass
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> <code>{e}</code>")

    await bot.send_message(
        user_id,
        "<b>Account Login Successfully.</b>\n\n"
        "If you get AUTH KEY issue, use /logout and /login again.",
    )


# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
