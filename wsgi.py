import asyncio
from bot import bot

# הגדרת event loop חדש
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# הפעלת הבוט ברקע
loop.create_task(bot.setup_and_run())

# יצוא האפליקציה עבור gunicorn
app = bot.web_app