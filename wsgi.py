import asyncio
from bot import DogWalkBot

# יצירת אובייקט הבוט
bot = DogWalkBot()

async def start_bot():
    """הפעלת הבוט והשרת במקביל"""
    await bot.run_bot()

# יצירת event loop והפעלת הבוט
loop = asyncio.get_event_loop()
loop.create_task(start_bot())

# יצוא האפליקציה עבור gunicorn
app = bot.web_app