import asyncio
from bot import DogWalkBot

# יצירת אובייקט הבוט הגלובלי
bot = DogWalkBot()

# הפעלת הבוט בתהליך נפרד
loop = asyncio.get_event_loop()
loop.create_task(bot.run_bot())

# יצוא האפליקציה עבור gunicorn
app = bot.web_app