import os
from pathlib import Path
from dotenv import load_dotenv

# טעינת משתני הסביבה
load_dotenv()

# הגדרת תיקיית הבסיס - משתמשים בתיקיית הפרויקט של Render
# /opt/render/project/src היא תיקייה עם הרשאות כתיבה ב-Render
BASE_DIR = Path("/opt/render/project/src" if os.path.exists("/opt/render/project/src") else os.getcwd())

# הגדרת תיקיות לנתונים וללוגים
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# יצירת התיקיות אם הן לא קיימות
for directory in [DATA_DIR, LOGS_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directory {directory}. Using base directory instead. Error: {e}")

# הגדרת נתיבים לקבצים
DATA_FILE = DATA_DIR / "dog_walks_data.json"
LOG_FILE = LOGS_DIR / "bot_log.log"

# הגדרות הבוט
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("No Telegram token found in environment variables")

# נתונים התחלתיים (אופציונלי) - משמשים רק בהפעלה ראשונה אם אין קובץ נתונים קיים
INITIAL_DATA = os.getenv('INITIAL_DATA')

# מילות מפתח לזיהוי טיולים
KEYWORDS = ["+40", "טיול", "יצאנו לטיול"]