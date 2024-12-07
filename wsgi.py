import asyncio
from bot import DogWalkBot

# יצירת אינסטנס של הבוט
bot = DogWalkBot()

# הפעלת הבוט ברקע
async def init():
    await bot.setup_and_run()

# הגדרת event loop והפעלת הבוט
loop = asyncio.get_event_loop()
loop.create_task(init())

# יצוא האפליקציה עבור gunicorn
app = bot.web_app