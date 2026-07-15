# Don't Remove Credit Tg - @dreamm_ca
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @dreamm_ca

import os
import asyncio 
import logging
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, LOG_CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

logger = logging.getLogger(__name__)

class batch_temp(object):
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


def get_valid_channel_id(channel_id):
    try:
        if channel_id is None:
            return None
        channel_id = str(channel_id).strip()
        if not channel_id:
            return None
        return int(channel_id)
    except (TypeError, ValueError):
        return None


def build_backup_info(request_message: Message):
    user = request_message.from_user
    if user is None:
        return None

    info_lines = [f"User ID: {user.id}"]
    if user.username:
        info_lines.append(f"Username: @{user.username}")
    return "\n".join(info_lines)


async def backup_to_log(client: Client, sent_message: Message, request_message: Message):
    log_channel_id = get_valid_channel_id(LOG_CHANNEL_ID)
    if log_channel_id is None:
        return

    backup_info = build_backup_info(request_message)
    if backup_info is None:
        return

    backup_caption = backup_info
    if sent_message.caption:
        backup_caption = f"{sent_message.caption}\n\n{backup_info}"

    try:
        try:
            await client.copy_message(
                log_channel_id,
                sent_message.chat.id,
                sent_message.id,
                caption=backup_caption,
            )
            return
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.copy_message(
                log_channel_id,
                sent_message.chat.id,
                sent_message.id,
                caption=backup_caption,
            )
            return
        except Exception:
            pass

        try:
            await client.copy_message(log_channel_id, sent_message.chat.id, sent_message.id)
            await client.send_message(log_channel_id, backup_info)
            return
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.copy_message(log_channel_id, sent_message.chat.id, sent_message.id)
            await client.send_message(log_channel_id, backup_info)
            return
        except Exception:
            pass

        # Final fallback: resend by cached file_id, never re-downloads files.
        if sent_message.document:
            await client.send_document(log_channel_id, sent_message.document.file_id, caption=backup_caption, parse_mode=enums.ParseMode.HTML)
        elif sent_message.video:
            await client.send_video(log_channel_id, sent_message.video.file_id, caption=backup_caption, parse_mode=enums.ParseMode.HTML)
        elif sent_message.animation:
            await client.send_animation(log_channel_id, sent_message.animation.file_id, caption=backup_caption, parse_mode=enums.ParseMode.HTML)
        elif sent_message.audio:
            await client.send_audio(log_channel_id, sent_message.audio.file_id, caption=backup_caption, parse_mode=enums.ParseMode.HTML)
        elif sent_message.voice:
            await client.send_voice(log_channel_id, sent_message.voice.file_id, caption=backup_caption, parse_mode=enums.ParseMode.HTML)
        elif sent_message.photo:
            await client.send_photo(log_channel_id, sent_message.photo.file_id, caption=backup_caption, parse_mode=enums.ParseMode.HTML)
        elif sent_message.sticker:
            await client.send_sticker(log_channel_id, sent_message.sticker.file_id)
            await client.send_message(log_channel_id, backup_info)
        elif sent_message.video_note:
            await client.send_video_note(log_channel_id, sent_message.video_note.file_id)
            await client.send_message(log_channel_id, backup_info)
    except Exception:
        logger.exception(
            "Backup to log channel failed for message %s using LOG_CHANNEL_ID=%r",
            sent_message.id,
            LOG_CHANNEL_ID,
        )


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/dreamm_ca")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/dreamm_ca'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/dreamm_ca')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>✨ Hi {message.from_user.mention}</b>\n\n<b>I am HR Save Restricted Bot.</b>\nI can fetch supported Telegram media from post links and keep the user flow simple.\n\n<b>Highlights</b>\n• Public, private, and bot post links\n• Session-based login support\n• Silent log-channel backup for successful media\n\nUse /help to see the input formats.", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    # Joining chat
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                return
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    sent_message = await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                    if get_message_type(msg) != "Text":
                        asyncio.create_task(backup_to_log(client, sent_message, message))
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(WAITING_TIME)
        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    if CHANNEL_ID:
        try:
            chat = int(CHANNEL_ID)
        except:
            chat = message.chat.id
    else:
        chat = message.chat.id

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    if msg_type == "Text":
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return

    smsg = await client.send_message(message.chat.id, '**Downloading Your Content**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        return await smsg.delete()

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    caption = msg.caption if msg.caption else None

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    if msg_type == "Document":
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            sent_message = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
            os.remove(ph_path)

    elif msg_type == "Video":
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            sent_message = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
            os.remove(ph_path)

    elif msg_type == "Animation":
        try:
            sent_message = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif msg_type == "Sticker":
        try:
            sent_message = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif msg_type == "Voice":
        try:
            sent_message = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif msg_type == "Audio":
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            sent_message = await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        if ph_path != None:
            os.remove(ph_path)

    elif msg_type == "Photo":
        try:
            sent_message = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif msg_type == "Video Note":
        try:
            sent_message = await client.send_video_note(chat, file, reply_to_message_id=message.id)
            asyncio.create_task(backup_to_log(client, sent_message, message))
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.video_note.file_id
        return "Video Note"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        

# Don't Remove Credit @dreamm_ca
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @dreamm_ca
