from time import ctime

from pyrogram import filters
from pyrogram.types import (InlineQuery, InlineQueryResultArticle,
                            InputTextMessageContent, Message)

from spr import SUDOERS, spr
from spr.utils.db import (add_chat, add_user, chat_exists,
                          get_blacklist_event, get_nsfw_count,
                          get_reputation, get_user_trust,
                          is_chat_blacklisted, is_user_blacklisted,
                          user_exists)

__MODULE__ = "💥 𝐈𝐧𝐟𝐨 💐"
__HELP__ = """
**ɢᴇᴛ ɪɴғᴏ ᴀʙᴏᴜᴛ ᴀ ᴄʜᴀᴛ ᴏʀ ᴜsᴇʀ**

/info [CHAT_ID/ᴜsᴇʀɴᴀᴍᴇ|USER_ID/ᴜsᴇʀɴᴀᴍᴇ]

ᴏʀ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ɪɴʟɪɴᴇ ᴍᴏᴅᴇ >>
@SpamProtection_Robot [CHAT_ID/ᴜsᴇʀɴᴀᴍᴇ|USER_ID/ᴜsᴇʀɴᴀᴍᴇ]
"""


async def get_user_info(user):
    try:
        user = await spr.get_users(user)
    except Exception:
        return
    if not user_exists(user.id):
        add_user(user.id)
    trust = get_user_trust(user.id)
    blacklisted = is_user_blacklisted(user.id)
    reason = None
    if blacklisted:
        reason, time = get_blacklist_event(user.id)
    data = f"""
**ɪᴅ:** {user.id}
**ᴅᴄ:** {user.dc_id}
**ᴜsᴇʀɴᴀᴍᴇ:** {user.username}
**ᴍᴇɴᴛɪᴏɴ: ** {user.mention("Link")}

**ɪs sᴜᴅᴏ:** {user.id in SUDOERS}
**ᴛʀᴜsᴛ:** {trust}
**sᴘᴀᴍᴍᴇʀ:** {True if trust < 50 else False}
**ʀᴇᴘᴜᴛᴀᴛɪᴏɴ:** {get_reputation(user.id)}
**ɴsғᴡ ᴄᴏᴜɴᴛ:** {get_nsfw_count(user.id)}
**ᴘᴏᴛᴇɴᴛɪᴀʟ sᴘᴀᴍᴍᴇʀ:** {True if trust < 70 else False}
**ʙʟᴀᴄᴋʟɪsᴛᴇᴅ:** {blacklisted}
"""
    data += (
        f"**ʙʟᴀᴄᴋʟɪsᴛ ʀᴇᴀsᴏɴ:** {reason} | {ctime(time)}"
        if reason
        else ""
    )
    return data


async def get_chat_info(chat):
    try:
        chat = await spr.get_chat(chat)
    except Exception:
        return
    if not chat_exists(chat.id):
        add_chat(chat.id)
    blacklisted = is_chat_blacklisted(chat.id)
    reason = None
    if blacklisted:
        reason, time = get_blacklist_event(chat.id)
    data = f"""
**ɪᴅ:** {chat.id}
**ᴜsᴇʀɴᴀᴍᴇ:** {chat.username}
**ᴛʏᴘᴇ:** {chat.type}
**ᴍᴇᴍʙᴇʀs:** {chat.members_count}
**sᴄᴀᴍ:** {chat.is_scam}
**ʀᴇsᴛʀɪᴄᴛᴇᴅ:** {chat.is_restricted}
**ʙʟᴀᴄᴋʟɪsᴛᴇᴅ:** {blacklisted}
"""
    data += (
        f"**ʙʟᴀᴄᴋʟɪsᴛ ʀᴇᴀsᴏɴ:** {reason} | {ctime(time)}"
        if reason
        else ""
    )
    return data


async def get_info(entity):
    user = await get_user_info(entity)
    if user:
        return user
    chat = await get_chat_info(entity)
    return chat


@spr.on_message(filters.command("info"), group=3)
async def info_func(_, message: Message):
    if message.reply_to_message:
        reply = message.reply_to_message
        user = reply.from_user
        entity = user.id or message.chat.id
    elif len(message.command) == 1:
        user = message.from_user
        entity = user.id or message.chat.id
    elif len(message.command) == 2:
        entity = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("ʀᴇᴀᴅ ᴛʜᴇ ʜᴇʟᴘ ᴍᴇɴᴜ...")
    entity = await get_info(entity)
    entity = entity or "ɪ ʜᴀᴠᴇɴ'ᴛ sᴇᴇɴ ᴛʜɪs ᴄʜᴀᴛ/ᴜsᴇʀ..."
    await message.reply_text(entity)


@spr.on_inline_query()
async def inline_info_func(_, query: InlineQuery):
    query_ = query.query.strip()
    entity = await get_info(query_)
    if not entity:
        err = "I ʜᴀᴠᴇɴ'ᴛ sᴇᴇɴ ᴛʜɪs ᴜsᴇʀ/ᴄʜᴀᴛ..."
        results = [
            InlineQueryResultArticle(
                err,
                input_message_content=InputTextMessageContent(err),
            )
        ]
    else:
        results = [
            InlineQueryResultArticle(
                "ғᴏᴜɴᴅ ᴇɴᴛɪᴛʏ...",
                input_message_content=InputTextMessageContent(entity),
            )
        ]
    await query.answer(results=results, cache_time=3)
