from pyrogram import Client, filters
from pyrogram.types import Message
from parsehub import ParseHub
from config.config import bot_cfg

@Client.on_message(filters.command(["start", "help"]))
async def start(cli: Client, msg: Message):
    if msg.from_user.id not in bot_cfg.allowed_users:
        return
    await msg.reply(get_supported_platforms())


def get_supported_platforms():
    return "**支持的平台:**\n\n" + "\n".join(ParseHub().get_supported_platforms())
