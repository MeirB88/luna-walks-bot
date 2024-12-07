import json
import os
from datetime import datetime
from pathlib import Path
import asyncio
import gc
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackContext
from config import TELEGRAM_TOKEN, KEYWORDS, DATA_FILE
from logger_config import setup_logger

# הגדרת מצבים לשיחה עם המשתמש
CONFIRM_DELETE = 1

class DogWalkBot:
    def __init__(self):
        """
        אתחול הבוט
        כולל הגדרת הלוגר, משתני המצב הבסיסיים ושרת האינטרנט
        """
        self.logger = setup_logger('DogWalkBot')
        self.token = TELEGRAM_TOKEN
        self.keywords = KEYWORDS
        self.walks_data = self.load_data()
        self.application = None
        self.cleanup_task = None
        self.web_app = self.setup_web_app()  # הגדרת שרת האינטרנט כבר באתחול
        self.logger.info("Bot initialized")
    
    def setup_web_app(self):
        """
        הגדרת שרת האינטרנט הבסיסי
        """
        app = web.Application()
        app.router.add_get("/", self.health_check)
        app.router.add_get("/health", self.health_check)
        return app

    async def health_check(self, request):
        """
        נקודת קצה לבדיקת תקינות
        """
        return web.Response(text="Bot is running!", status=200)

    [... שאר הקוד נשאר זהה לגרסה הקודמת ...]

    async def run_bot(self):
        """
        הפעלת הבוט
        """
        try:
            # הגדרת האפליקציה
            self.application = Application.builder().token(self.token).build()
            
            # הגדרת Conversation Handler למחיקת נתונים
            delete_conv_handler = ConversationHandler(
                entry_points=[CommandHandler('del', self.del_command)],
                states={
                    CONFIRM_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm_delete)]
                },
                fallbacks=[]
            )
            
            # הוספת handlers
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("test", self.test))
            self.application.add_handler(CommandHandler("sum", self.generate_summary))
            self.application.add_handler(delete_conv_handler)
            self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_message
            ))
            
            # הפעלת משימת ניקוי הזיכרון התקופתית
            self.cleanup_task = asyncio.create_task(self.periodic_cleanup())
            self.logger.info("Memory cleanup task started")
            
            # הפעלת הבוט
            self.logger.info("Starting bot...")
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            self.logger.error(f"Error running bot: {str(e)}")
            raise e

# יצירת אובייקט הבוט הגלובלי - חשוב עבור gunicorn
bot = DogWalkBot()

if __name__ == "__main__":
    # הפעלת הבוט רק אם מריצים את הקובץ ישירות
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.run_bot())
    except KeyboardInterrupt:
        bot.logger.info("Bot stopped by user")
    except Exception as e:
        bot.logger.error(f"Bot stopped due to error: {str(e)}")
    finally:
        loop.close()