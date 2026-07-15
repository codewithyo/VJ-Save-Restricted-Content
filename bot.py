# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client
from pyrogram.types import BotCommand
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM, LOG_CHANNEL_ID
from pathlib import Path
import hashlib


def get_valid_log_channel_id(channel_id):
    try:
        if channel_id is None:
            return None
        channel_id = str(channel_id).strip()
        if not channel_id:
            return None
        return int(channel_id)
    except (TypeError, ValueError):
        return None


def file_sha1(path):
    try:
        content = Path(path).read_bytes()
        return hashlib.sha1(content).hexdigest()[:10]
    except Exception:
        return "unknown"

if STRING_SESSION is not None and LOGIN_SYSTEM == False:
	TechVJUser = Client("TechVJ", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
	TechVJUser.start()
else:
    TechVJUser = None

class Bot(Client):

    def __init__(self):
        super().__init__(
            "techvj login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=150,
            sleep_threshold=5
        )

      
    async def start(self):
            
        await super().start()
        print('Bot Started Powered By @dreamm_ca')
        print(f"Build Fingerprint: start={file_sha1('TechVJ/start.py')} generate={file_sha1('TechVJ/generate.py')} bot={file_sha1('bot.py')}")
        log_channel_id = get_valid_log_channel_id(LOG_CHANNEL_ID)
        if log_channel_id is None:
            print('Backup Channel: DISABLED (LOG_CHANNEL_ID is missing or invalid)')
        else:
            print(f'Backup Channel: ENABLED ({log_channel_id})')
        try:
            await self.set_bot_commands([
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Show help"),
                BotCommand("generate", "Generate API ID and API HASH"),
                BotCommand("login", "Login your account"),
                BotCommand("logout", "Logout your session"),
                BotCommand("cancel", "Cancel ongoing task"),
                BotCommand("broadcast", "Broadcast message (admin only)"),
            ])
            print('Bot menu commands updated')
        except Exception as e:
            print(f'Failed to update bot menu commands: {e}')

    async def stop(self, *args):

        await super().stop()
        print('Bot Stopped Bye')

if __name__ == "__main__":
    bot = Bot()
    bot.run()

# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
