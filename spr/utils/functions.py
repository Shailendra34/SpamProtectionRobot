from time import ctime

from pyrogram.errors import (ChatAdminRequired, ChatWriteForbidden,
                             UserAdminInvalid)
from pyrogram.types import Message

from spr import NSFW_LOG_CHANNEL, SPAM_LOG_CHANNEL, spr
from spr.core import ikb
from spr.utils.db import (get_blacklist_event, get_nsfw_count,
                          get_reputation, get_user_trust,
                          increment_nsfw_count, is_user_blacklisted)


async def get_user_info(message):
    user = message.from_user
    trust = get_user_trust(user.id)
    user_ = f"{('@' + user.username) if user.username else user.mention} [`{user.id}`]"
    blacklisted = is_user_blacklisted(user.id)
    reason = None
    if blacklisted:
        reason, time = get_blacklist_event(user.id)
    data = f"""
**ᴜsᴇʀ:**
    **ᴜsᴇʀɴᴀᴍᴇ:** {user_}
    **ᴛʀᴜsᴛ:** {trust}
    **sᴘᴀᴍᴍᴇʀ:** {True if trust < 50 else False}
    **ʀᴇᴘᴜᴛᴀᴛɪᴏɴ:** {get_reputation(user.id)}
    **ɴsғᴡ ᴄᴏᴜɴᴛ:** {get_nsfw_count(user.id)}
    **ᴘᴏᴛᴇɴᴛɪᴀʟ Spammer:** {True if trust < 70 else False}
    **ʙʟᴀᴄᴋʟɪsᴛᴇᴅ:** {is_user_blacklisted(user.id)}
"""
    data += (
        f"    **ʙʟᴀᴄᴋʟɪsᴛ ʀᴇᴀsᴏɴ:** {reason} | {ctime(time)}"
        if reason
        else ""
    )
    return data


async def delete_get_info(message: Message):
    try:
        await message.delete()
    except (ChatAdminRequired, UserAdminInvalid):
        try:
            return await message.reply_text(
                "ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴇʟᴇᴛᴇ "
                + "ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡʜɪᴄʜ ɪs ғʟᴀɢɢᴇᴅ ᴀs sᴘᴀᴍ..."
            )
        except ChatWriteForbidden:
            return await spr.leave_chat(message.chat.id)
    return await get_user_info(message)


async def delete_nsfw_notify(
    message: Message,
    result,
):
    await message.copy(
        NSFW_LOG_CHANNEL,
        reply_markup=ikb(
            {"Correct": "upvote_nsfw", "Incorrect": "downvote_nsfw"}
        ),
    )
    info = await delete_get_info(message)
    if not info:
        return
    msg = f"""
🚨 **ɴsғᴡ ᴀʟᴇʀᴛ**  🚔
{info}
**ᴘʀᴇᴅɪᴄᴛɪᴏɴ:**
    **sᴀғᴇ:** `{result.neutral} %`
    **ᴘᴏʀɴ:** `{result.porn} %`
    **ᴀᴅᴜʟᴛ:** `{result.sexy} %`
    **ʜᴇɴᴛᴀɪ:** `{result.hentai} %`
    **ᴅʀᴀᴡɪɴɢs:** `{result.drawings} %`
"""
    await spr.send_message(message.chat.id, text=msg)
    increment_nsfw_count(message.from_user.id)


async def delete_spam_notify(
    message: Message,
    spam_probability: float,
):
    info = await delete_get_info(message)
    if not info:
        return
    msg = f"""
🚨 **sᴘᴀᴍ ᴀʟᴇʀᴛ**  🚔
{info}
**sᴘᴀᴍ ᴘʀᴏʙᴀʙɪʟɪᴛʏ:** {spam_probability} %

__ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ__
"""
    content = message.text or message.caption
    content = content[:400] + "..."
    report = f"""
**sᴘᴀᴍ ᴅᴇᴛᴇᴄᴛɪᴏɴ**
{info}
**ᴄᴏɴᴛᴇɴᴛ:**
{content}
    """

    keyb = ikb(
        {
            "Correct (0)": "upvote_spam",
            "Incorrect (0)": "downvote_spam",
            "Chat": "https://t.me/" + (message.chat.username or "SpamProtectionLog/93"),
        },
        2
    )
    m = await spr.send_message(
        SPAM_LOG_CHANNEL,
        report,
        reply_markup=keyb,
        disable_web_page_preview=True,
    )

    keyb = ikb({"View Message": m.link})
    await spr.send_message(
        message.chat.id, text=msg, reply_markup=keyb
    )


async def kick_user_notify(message: Message):
    try:
        await spr.ban_chat_member(
            message.chat.id, message.from_user.id
        )
    except (ChatAdminRequired, UserAdminInvalid):
        try:
            return await message.reply_text(
                "ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ʙᴀɴ "
                + "ᴛʜɪs ᴜsᴇʀ ᴡʜᴏ ɪs ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴀɴᴅ ғʟᴀɢɢᴇᴅ ᴀs sᴘᴀᴍᴍᴇʀ..."
            )
        except ChatWriteForbidden:
            return await spr.leave_chat(message.chat.id)
    info = await get_user_info(message)
    msg = f"""
🚨 **sᴘᴀᴍᴍᴇʀ ᴀʟᴇʀᴛ**  🚔
{info}

__ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ__
"""
    await spr.send_message(message.chat.id, msg)
