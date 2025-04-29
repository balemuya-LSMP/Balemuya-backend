# handlers/start_handler.py

from .base_handler import BaseHandler
from ..utils import generate_keyboard

class StartHandler(BaseHandler):
    def handle(self):
        self.auth_service.clear_session()
        self.bot_service.send_message(
            self.chat_id,
            "👋 Welcome to Balemuya!\nPlease choose an option:",
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help", "❌ Cancel"]])
        )
        return {"status": "ok"}
