from os import remove

from pyrogram import filters
from pyrogram.types import Message

from spr import SUDOERS, arq, spr
from spr.utils.db import (disable_nsfw, disable_spam, enable_nsfw,
                          enable_spam, is_nsfw_enabled,
                          is_spam_enabled)
from spr.utils.misc import admins, get_file_id

__MODULE__ = "⭐ 𝐌𝐚𝐧𝐚𝐠𝐞 ⚡"
__HELP__ = """
/anti_nsfw [ENABLE|DISABLE] - ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ɴsғᴡ ᴅᴇᴛᴇᴄᴛɪᴏɴ...
/anti_spam [ENABLE|DISABLE] - ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ sᴘᴀᴍ ᴅᴇᴛᴇᴄᴛɪᴏɴ...

/nsfw_scan - ᴄʟᴀssɪғʏ ᴀ ᴍᴇᴅɪᴀ.
/spam_scan - ɢᴇᴛ sᴘᴀᴍ ᴘʀᴇᴅɪᴄᴛɪᴏɴs ᴏғ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ...
"""


@spr.on_message(
    filters.command("anti_nsfw") & ~filters.private, group=3
)
async def nsfw_toggle_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "ᴜsᴀɢᴇ: /anti_nsfw [ENABLE|DISABLE]"
        )
    if message.from_user:
        user = message.from_user
        chat_id = message.chat.id
        if user.id not in SUDOERS and user.id not in (
            await admins(chat_id)
        ):
            return await message.reply_text(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴs..."
            )
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "enable":
        if is_nsfw_enabled(chat_id):
            return await message.reply("ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ...")
        enable_nsfw(chat_id)
        await message.reply_text("ᴇɴᴀʙʟᴇᴅ ɴsғᴡ ᴅᴇᴛᴇᴄᴛɪᴏɴ...")
    elif status == "disable":
        if not is_nsfw_enabled(chat_id):
            return await message.reply("ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ...")
        disable_nsfw(chat_id)
        await message.reply_text("ᴅɪsᴀʙʟᴇᴅ ɴsғᴡ ᴅᴇᴛᴇᴄᴛɪᴏɴ...")
    else:
        await message.reply_text(
            "ᴜɴᴋɴᴏᴡɴ sᴜғғɪx, ᴜsᴇ /anti_nsfw [ENABLE|DISABLE]"
        )


@spr.on_message(
    filters.command("anti_spam") & ~filters.private, group=3
)
async def spam_toggle_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "ᴜsᴀɢᴇ: /anti_spam [ENABLE|DISABLE]"
        )
    if message.from_user:
        user = message.from_user
        chat_id = message.chat.id
        if user.id not in SUDOERS and user.id not in (
            await admins(chat_id)
        ):
            return await message.reply_text(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴs..."
            )
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "enable":
        if is_spam_enabled(chat_id):
            return await message.reply("ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ...")
        enable_spam(chat_id)
        await message.reply_text("ᴇɴᴀʙʟᴇᴅ sᴘᴀᴍ ᴅᴇᴛᴇᴄᴛɪᴏɴ...")
    elif status == "disable":
        if not is_spam_enabled(chat_id):
            return await message.reply("ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ...")
        disable_spam(chat_id)
        await message.reply_text("ᴅɪsᴀʙʟᴇᴅ sᴘᴀᴍ ᴅᴇᴛᴇᴄᴛɪᴏɴ...")
    else:
        await message.reply_text(
            "ᴜɴᴋɴᴏᴡɴ sᴜғғɪx, ᴜsᴇ /anti_spam [ENABLE|DISABLE]"
        )


@spr.on_message(filters.command("nsfw_scan"), group=3)
async def nsfw_scan_command(_, message: Message):
    err = "ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ/ᴅᴏᴄᴜᴍᴇɴᴛ/sᴛɪᴄᴋᴇʀ/ᴀɴɪᴍᴀᴛɪᴏɴ ᴛᴏ sᴄᴀɴ ɪᴛ..."
    if not message.reply_to_message:
        await message.reply_text(err)
        return
    reply = message.reply_to_message
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        await message.reply_text(err)
        return
    m = await message.reply_text("sᴄᴀɴɴɪɴɢ...")
    file_id = get_file_id(reply)
    if not file_id:
        return await m.edit("sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...")
    file = await spr.download_media(file_id)
    try:
        results = await arq.nsfw_scan(file=file)
    except Exception as e:
        return await m.edit(str(e))
    remove(file)
    if not results.ok:
        return await m.edit(results.result)
    results = results.result
    await m.edit(
        f"""
**ɴᴇᴜᴛʀᴀʟ:** `{results.neutral} %`
**ᴘᴏʀɴ:** `{results.porn} %`
**ʜᴇɴᴛᴀɪ:** `{results.hentai} %`
**sᴇxʏ:** `{results.sexy} %`
**ᴅʀᴀᴡɪɴɢs:** `{results.drawings} %`
**ɴsғᴡ:** `{results.is_nsfw}`
"""
    )


@spr.on_message(filters.command("spam_scan"), group=3)
async def scanNLP(_, message: Message):
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴄᴀɴ ɪᴛ...")
    r = message.reply_to_message
    text = r.text or r.caption
    if not text:
        return await message.reply("ᴄᴀɴ'ᴛ sᴄᴀɴ ᴛʜᴀᴛ...")
    data = await arq.nlp(text)
    data = data.result[0]
    msg = f"""
**ɪs sᴘᴀᴍ:** {data.is_spam}
**sᴘᴀᴍ ᴘʀᴏʙᴀʙɪʟɪᴛʏ:** {data.spam_probability} %
**sᴘᴀᴍ:** {data.spam}
**ʜᴀᴍ:** {data.ham}
**ᴘʀᴏғᴀɴɪᴛʏ:** {data.profanity}
"""
    await message.reply(msg, quote=True)
