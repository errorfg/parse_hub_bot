# bot.py
from pyrogram import Client
from config.config import bot_cfg
from log import logger
import asyncio
from telethon_client import TelethonClient

logger.add("logs/bot.log", rotation="10 MB")

class Bot(Client):
    def __init__(self):
        self.cfg = bot_cfg
        self.telethon = TelethonClient()

        super().__init__(
            name=f'{self.cfg.bot_token.split(":")[0]}_bot',
            api_id=self.cfg.api_id,
            api_hash=self.cfg.api_hash,
            bot_token=self.cfg.bot_token,
            plugins=dict(root="plugins"),
            proxy=self.cfg.proxy.dict_format,
        )

    async def start(self):
        await super().start()
        logger.info("Pyrogram Bot开始运行...")
        # 启动 Telethon 客户端
        await self.telethon.start(self)

    async def stop(self, *args):
        await self.telethon.stop()
        await super().stop()

async def main():
    bot = Bot()
    await bot.start()
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())