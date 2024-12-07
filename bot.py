import json
from datetime import datetime
from pathlib import Path
import asyncio
import gc  # יבוא מודול garbage collector לניהול זיכרון
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
        """
        self.logger = setup_logger('DogWalkBot')
        self.token = TELEGRAM_TOKEN
        self.keywords = KEYWORDS
        self.walks_data = self.load_data()
        self.application = None
        self.cleanup_task = None  # משתנה חדש לשמירת המשימה של ניקוי הזיכרון
        self.logger.info("Bot initialized")
    
    async def periodic_cleanup(self):
        """
        פונקציה חדשה שמבצעת ניקוי זיכרון תקופתי.
        רצה כל שעה ומנקה זיכרון שלא בשימוש כדי למנוע דליפות.
        """
        while True:
            try:
                # המתנה של שעה בין ניקויים
                await asyncio.sleep(3600)
                
                # הפעלת garbage collector באופן מפורש
                collected = gc.collect()
                
                # תיעוד תוצאות הניקוי
                self.logger.info(f"Memory cleanup completed - {collected} objects collected")
                
            except Exception as e:
                self.logger.error(f"Error during memory cleanup: {str(e)}")
    
    def load_data(self) -> dict:
        """
        טעינת נתונים מקובץ JSON
        """
        try:
            if DATA_FILE.exists():
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info("Data loaded successfully")
                    return data
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
        
        # יצירת מבנה ברירת מחדל
        default_data = {
            "users": {},
            "current_month": datetime.now().strftime("%Y-%m")
        }
        self.logger.info("Created new data structure")
        return default_data
    
    def save_data(self):
        """
        שמירת נתונים לקובץ JSON
        """
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.walks_data, f, ensure_ascii=False, indent=2)
            self.logger.info("Data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")

    def get_display_name(self, original_name: str) -> str:
        """
        המרת שמות משתמשים מיוחדים
        """
        if original_name == "nothing":
            return "מאיר"
        elif original_name == "Mati Noah":
            return "רות"
        return original_name
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        טיפול בפקודת /start
        """
        self.logger.info(f"Start command received from user {update.effective_user.id}")
        await update.message.reply_text("ברוכים הבאים לבוט מעקב טיולי כלבים! 🐕")
    
    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        טיפול בפקודת /test
        """
        self.logger.info(f"Test command received from user {update.effective_user.id}")
        await update.message.reply_text("הבוט פעיל ועובד! 🐾")

    async def generate_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        טיפול בפקודת /sum - יצירת דוח סיכום
        """
        self.logger.info(f"Summary command received from user {update.effective_user.id}")
        summary = self.calculate_monthly_summary()
        
        # יצירת הודעת סיכום
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
        """
        חישוב סיכום חודשי של טיולים ותשלומים
        """
        summary = {}
        for user_id, data in self.walks_data["users"].items():
            walks = data.get("walks", 0)
            total_amount = walks * 40  # כל טיול שווה 40 ש"ח
            
            # המרת שמות משתמשים מיוחדים
            name = self.get_display_name(data.get("name", "משתמש לא ידוע"))
            
            summary[user_id] = {
                "name": name,
                "walks": walks,
                "amount": total_amount
            }
        
        # מציאת המנצח
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
        """
        טיפול בפקודת /del - התחלת תהליך מחיקת נתונים
        """
        self.logger.info(f"Delete command received from user {update.effective_user.id}")
        await update.message.reply_text(
            "🚨 האם אתה בטוח שברצונך למחוק את כל נתוני הטיולים?\n"
            "ענה 'כן' לאישור או 'לא' לביטול"
        )
        return CONFIRM_DELETE

    async def confirm_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        טיפול באישור מחיקת נתונים
        """
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
        """
        טיפול בפקודות לא מוכרות
        """
        self.logger.info(f"Unknown command received: {update.message.text}")
        await update.message.reply_text("❌ פקודה לא מוכרת")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        טיפול בהודעות רגילות
        """
        if not update.message or not update.message.text:
            self.logger.warning("Received update without message or text")
            return

        text = update.message.text.lower()
        user_id = str(update.effective_user.id)
        original_name = update.effective_user.full_name
        display_name = self.get_display_name(original_name)
        
        self.logger.info(f"Message received: '{text}' from {display_name} ({user_id})")
        
        # בדיקת מילות מפתח
        if any(keyword.lower() in text for keyword in self.keywords):
            self.logger.info(f"Keyword found in message from {display_name}")
            
            # עדכון נתונים
            if user_id not in self.walks_data["users"]:
                self.walks_data["users"][user_id] = {"name": original_name, "walks": 0}
            
            self.walks_data["users"][user_id]["walks"] += 1
            self.save_data()
            
            # שליחת אישור
            await update.message.reply_text(
                f"✅ נרשם טיול חדש!\n"
                f"🦮 מספר טיולים החודש: {self.walks_data['users'][user_id]['walks']}"
            )
    
    def run(self):
        """
        הפעלת הבוט
        התוספת החדשה היא הפעלת משימת ניקוי הזיכרון התקופתית
        """
        try:
            # יצירת האפליקציה
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
            
            # Handler לפקודות לא מוכרות - חייב להיות אחרון!
            self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
            
            # Handler להודעות רגילות
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_message
            ))
            
            # הפעלת משימת ניקוי הזיכרון התקופתית
            self.cleanup_task = asyncio.create_task(self.periodic_cleanup())
            self.logger.info("Memory cleanup task started")
            
            # הפעלת הבוט
            self.logger.info("Starting bot...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            self.logger.error(f"Error running bot: {str(e)}")
            raise e

if __name__ == "__main__":
    bot = DogWalkBot()
    bot.run()