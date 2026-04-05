import json
import logging
import os
from typing import Any

logger = logging.getLogger("consumption_router.config")


class ConfigManager:
    def __init__(self, config_path: str | None = None):
        if not config_path:
            user_profile = os.environ.get("USERPROFILE", "")
            config_path = os.path.join(user_profile, ".gemini", "antigravity", "mcp_config.json")

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}")
            return {}

        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def get_mcp_servers(self) -> dict[str, Any]:
        return self.config.get("mcpServers", {})

    def get_server_config(self, server_name: str) -> dict[str, Any] | None:
        return self.get_mcp_servers().get(server_name)
