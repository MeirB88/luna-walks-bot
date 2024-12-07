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
        אתחול הבוט והגדרת המשתנים הבסיסיים
        מגדיר את הלוגר, מאתחל את ה-web app ומכין את כל הדברים הנדרשים
        """
        self.logger = setup_logger('DogWalkBot')
        self.token = TELEGRAM_TOKEN
        self.keywords = KEYWORDS
        self.walks_data = self.load_data()
        self.application = None
        self.cleanup_task = None
        
        # הגדרת שרת האינטרנט
        self.web_app = web.Application()
        self.web_app.router.add_get("/", self.health_check)
        self.web_app.router.add_get("/health", self.health_check)
        
        self.logger.info("Bot initialized")
    
    async def setup_and_run(self):
        """
        פונקציה שמאתחלת ומפעילה את הבוט
        כוללת את כל ההגדרות וההפעלה של הבוט
        """
        try:
            # הגדרת הבוט
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
            
            # אתחול והפעלת הבוט
            await self.application.initialize()
            await self.application.start()
            
            # הפעלת משימת ניקוי הזיכרון התקופתית
            self.cleanup_task = asyncio.create_task(self.periodic_cleanup())
            self.logger.info("Bot setup completed")
            
            # הפעלת הפולינג
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            self.logger.info("Bot polling started")
            
            # שמירה על הבוט פעיל
            while True:
                await asyncio.sleep(3600)  # בדיקה כל שעה
                
        except Exception as e:
            self.logger.error(f"Error in setup_and_run: {str(e)}")
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            raise e
    
    async def health_check(self, request):
        """
        נקודת קצה לבדיקת תקינות הבוט
        """
        status = "Bot is running"
        if self.application and self.application.updater.running:
            status += " and polling"
        return web.Response(text=status)
    
    async def periodic_cleanup(self):
        """
        פונקציה שמבצעת ניקוי זיכרון תקופתי
        רצה כל שעה ומנקה זיכרון שלא בשימוש
        """
        while True:
            try:
                await asyncio.sleep(3600)  # המתנה של שעה
                collected = gc.collect()    # הפעלת garbage collector
                self.logger.info(f"Memory cleanup completed - {collected} objects collected")
            except Exception as e:
                self.logger.error(f"Error during memory cleanup: {str(e)}")
    
    def load_data(self) -> dict:
        """טעינת נתונים מקובץ JSON"""
        try:
            if DATA_FILE.exists():
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info("Data loaded successfully")
                    return data
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
        
        default_data = {
            "users": {},
            "current_month": datetime.now().strftime("%Y-%m")
        }
        self.logger.info("Created new data structure")
        return default_data
    
    def save_data(self):
        """שמירת נתונים לקובץ JSON"""
        try:
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.walks_data, f, ensure_ascii=False, indent=2)
            self.logger.info("Data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")

    def get_display_name(self, original_name: str) -> str:
        """המרת שמות משתמשים מיוחדים"""
        if original_name == "nothing":
            return "מאיר"
        elif original_name == "Mati Noah":
            return "רות"
        return original_name
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודת /start"""
        self.logger.info(f"Start command received from user {update.effective_user.id}")
        await update.message.reply_text("ברוכים הבאים לבוט מעקב טיולי כלבים! 🐕")
    
    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודת /test"""
        self.logger.info(f"Test command received from user {update.effective_user.id}")
        await update.message.reply_text("הבוט פעיל ועובד! 🐾")

    async def generate_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """יצירת דוח סיכום חודשי"""
        self.logger.info(f"Summary command received from user {update.effective_user.id}")
        summary = self.calculate_monthly_summary()
        
        message = "📊 סיכום טיולים חודשי:\n\n"
        
        for user_id, data in summary.items():
            if user_id != "settlement":
                message += f"👤 {data['name']}:\n"
                message += f"🦮 מספר טיולים: {data['walks']}\n"
                message += f"💰 סכום כולל: {data['amount']} ₪\n\n"
        
        if "settlement" in summary:
            message += f"🏆 המנצח: {summary['settlement']['winner']}\n"
            message += f"💸 סכום להעברה: {summary['settlement']['amount']} ₪"
        
        await update.message.reply_text(message)

    def calculate_monthly_summary(self) -> dict:
        """חישוב סיכום חודשי של טיולים ותשלומים"""
        summary = {}
        for user_id, data in self.walks_data["users"].items():
            walks = data.get("walks", 0)
            total_amount = walks * 40
            name = self.get_display_name(data.get("name", "משתמש לא ידוע"))
            
            summary[user_id] = {
                "name": name,
                "walks": walks,
                "amount": total_amount
            }
        
        if len(summary) >= 2:
            amounts = [(user_id, data["amount"]) for user_id, data in summary.items()]
            winner = max(amounts, key=lambda x: x[1])
            loser = min(amounts, key=lambda x: x[1])
            difference = (winner[1] - loser[1]) / 2
            summary["settlement"] = {
                "winner": summary[winner[0]]["name"],
                "amount": difference
            }
        
        return summary

    async def del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """התחלת תהליך מחיקת נתונים"""
        self.logger.info(f"Delete command received from user {update.effective_user.id}")
        await update.message.reply_text(
            "🚨 האם אתה בטוח שברצונך למחוק את כל נתוני הטיולים?\n"
            "ענה 'כן' לאישור או 'לא' לביטול"
        )
        return CONFIRM_DELETE

    async def confirm_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול באישור מחיקת נתונים"""
        response = update.message.text.strip()
        
        if response == 'כן':
            self.walks_data["users"] = {}
            self.save_data()
            self.logger.info(f"Data deleted by user {update.effective_user.id}")
            await update.message.reply_text("✅ כל הנתונים נמחקו בהצלחה")
        else:
            self.logger.info(f"Data deletion cancelled by user {update.effective_user.id}")
            await update.message.reply_text("❌ פעולת המחיקה בוטלה")
        
        return ConversationHandler.END

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודות לא מוכרות"""
        self.logger.info(f"Unknown command received: {update.message.text}")
        await update.message.reply_text("❌ פקודה לא מוכרת")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בהודעות רגילות וזיהוי טיולים"""
        if not update.message or not update.message.text:
            self.logger.warning("Received update without message or text")
            return

        text = update.message.text.lower()
        user_id = str(update.effective_user.id)
        original_name = update.effective_user.full_name
        display_name = self.get_display_name(original_name)
        
        self.logger.info(f"Message received: '{text}' from {display_name} ({user_id})")
        
        if any(keyword.lower() in text for keyword in self.keywords):
            self.logger.info(f"Keyword found in message from {display_name}")
            
            if user_id not in self.walks_data["users"]:
                self.walks_data["users"][user_id] = {"name": original_name, "walks": 0}
            
            self.walks_data["users"][user_id]["walks"] += 1
            self.save_data()
            
            await update.message.reply_text(
                f"✅ נרשם טיול חדש!\n"
                f"🦮 מספר טיולים החודש: {self.walks_data['users'][user_id]['walks']}"
            )

# יצירת אינסטנס גלובלי של הבוט
bot = DogWalkBot()

if __name__ == "__main__":
    # הרצה ישירה של הבוט (לא דרך gunicorn)
    asyncio.run(bot.setup_and_run())