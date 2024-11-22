# config/config.py
from urllib.parse import urlparse
from dotenv import load_dotenv
from os import getenv
from typing import Optional, List

load_dotenv()

class BotConfig:
    class _Proxy:
        def __init__(self, url: str):
            self._url = urlparse(url) if url else None
            self.url = self._url.geturl() if self._url else None

        @property
        def dict_format(self):
            if not self._url:
                return None
            return {
                "scheme": self._url.scheme,
                "hostname": self._url.hostname,
                "port": self._url.port,
                "username": self._url.username,
                "password": self._url.password,
            }

    def __init__(self):
        # 基础配置
        self.bot_token = getenv("BOT_TOKEN")
        self.api_id = getenv("API_ID")
        self.api_hash = getenv("API_HASH")
        self.proxy: Optional[BotConfig._Proxy] = self._Proxy(getenv("PROXY", None))

        # 功能配置
        self.cache_time = int(ct) if (ct := getenv("CACHE_TIME")) else 600
        self.ai_summary = bool(getenv("AI_SUMMARY", "").lower() == "true")
        self.douyin_api = getenv("DOUYIN_API", None)

        # 权限控制配置
        self._parse_auth_config()
        
        # 自动解析配置
        self.auto_parse = bool(getenv("AUTO_PARSE", "true").lower() == "true")
        self.auto_parse_platforms = self._parse_platforms(getenv("AUTO_PARSE_PLATFORMS", "xiaohongshu"))
        self.telethon_session = getenv("TELETHON_SESSION")

    def _parse_auth_config(self):
        """解析权限配置"""
        # 允许的用户ID列表，格式：123456,789012
        allowed_users = getenv("ALLOWED_USERS", "")
        self.allowed_users = [int(uid.strip()) for uid in allowed_users.split(",") if uid.strip()] if allowed_users else []

        # 允许的群组ID列表，格式：-100123456789,-100987654321
        allowed_groups = getenv("ALLOWED_GROUPS", "")
        self.allowed_groups = [int(gid.strip()) for gid in allowed_groups.split(",") if gid.strip()] if allowed_groups else []

    def _parse_platforms(self, platforms_str: str) -> List[str]:
        """解析支持的平台列表"""
        return [p.strip().lower() for p in platforms_str.split(",") if p.strip()]


bot_cfg = BotConfig()