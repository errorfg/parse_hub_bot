# telethon_client.py
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
from config.config import bot_cfg
from log import logger
from methods import TgParseHub
from utiles.utile import progress

async def callback(current, total, status: str, msg):
    """进度回调适配器"""
    text = progress(current, total, status)
    if not text or msg.text == text:
        return
    await msg.edit_text(text)
    msg.text = text

class TelethonClient:
    def __init__(self):
        self.cfg = bot_cfg
        self.client = TelegramClient(
            'user_session',
            api_id=int(self.cfg.api_id),
            api_hash=self.cfg.api_hash,
            proxy=self.cfg.proxy.dict_format if self.cfg.proxy.dict_format else None
        )
        self.pyrogram_bot = None

    async def start(self, pyrogram_bot):
        """启动 Telethon 客户端"""
        self.pyrogram_bot = pyrogram_bot
        await self.client.start()
        logger.info("Telethon 客户端已启动")
        await self._setup_handlers()

    async def _setup_handlers(self):
        """设置消息处理器"""
        @self.client.on(events.NewMessage(chats=self.cfg.allowed_groups))
        async def handle_new_message(event):
            try:
                # 检查消息发送者是否为机器人
                sender = await event.get_sender()
                if not getattr(sender, 'bot', False):
                    return

                message = event.message
                links = []
                
                # 从消息实体中获取链接
                for entity, text in message.get_entities_text():
                    if isinstance(entity, MessageEntityTextUrl):
                        links.append(entity.url)
                    elif isinstance(entity, MessageEntityUrl):
                        links.append(text)

                if not links:
                    return

                logger.info(
                    f"\n收到机器人消息:\n"
                    f"Bot: {sender.username}\n"
                    f"提取到的链接: {links}\n"
                    f"------------------"
                )

                # 处理每个链接
                for link in links:
                    try:
                        tph = TgParseHub()
                        t = (
                            "已有相同任务正在解析, 等待解析完成..."
                            if await tph.get_parse_task(link)
                            else "解 析 中..."
                        )
                        # 使用 Pyrogram 客户端发送回复
                        chat_id = event.chat_id
                        message_id = event.message.id
                        r_msg = await self.pyrogram_bot.send_message(
                            chat_id=chat_id,
                            text=t,
                            reply_to_message_id=message_id
                        )

                        pp = await tph.parse(link)
                        await pp.download(callback, (r_msg,))

                    except Exception as e:
                        logger.error(f"处理链接 {link} 时出错: {str(e)}")
                        continue
                    else:
                        await r_msg.edit_text("上 传 中...")
                        try:
                            await pp.chat_upload(self.pyrogram_bot, r_msg)
                        except Exception as e:
                            await r_msg.edit_text("上传失败")
                            logger.error(f"上传链接 {link} 时出错: {str(e)}")
                            continue
                        await r_msg.delete()
                    
            except Exception as e:
                logger.error(f"Error: {str(e)}")

    async def stop(self):
        """停止客户端"""
        if self.client:
            await self.client.disconnect()