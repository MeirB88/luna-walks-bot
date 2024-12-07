from aiohttp import web
from bot import bot

async def start_background_tasks(app):
    """
    הפעלת משימות רקע (כמו הבוט) כשהשרת עולה
    """
    app['bot_task'] = app.loop.create_task(bot.setup_and_run())

async def cleanup_background_tasks(app):
    """
    ניקוי משימות רקע כשהשרת נסגר
    """
    if bot.application:
        try:
            await bot.application.stop()
            await bot.application.shutdown()
        except Exception as e:
            print(f"Error during cleanup: {e}")

# הוספת הפונקציות למחזור החיים של השרת
bot.web_app.on_startup.append(start_background_tasks)
bot.web_app.on_cleanup.append(cleanup_background_tasks)

# יצוא האפליקציה עבור gunicorn
app = bot.web_app