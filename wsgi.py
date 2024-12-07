import asyncio
from bot import bot

# הגדרת event loop חדש
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# פונקציה שמפעילה את הבוט ומחכה שהוא יתחיל לעבוד
async def init_bot():
    try:
        await bot.setup_and_run()
    except Exception as e:
        print(f"Error starting bot: {e}")
        raise e

# הפעלת הבוט בתהליך הרקע
loop.create_task(init_bot())

# יצוא האפליקציה עבור gunicorn
app = bot.web_app

# וידוא שה-loop רץ
if not loop.is_running():
    loop.run_forever()