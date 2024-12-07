import os
from pathlib import Path
from dotenv import load_dotenv

# טעינת משתני הסביבה
load_dotenv()

# הגדרת נתיבים באופן שיעבוד גם ב-Render
BASE_DIR = Path(__file__).parent
LOGS_DIR = Path(os.getenv('LOG_DIR', BASE_DIR / "logs"))
DATA_FILE = Path(os.getenv('DATA_FILE', BASE_DIR / "dog_walks_data.json"))

# יצירת תיקיית לוגים אם לא קיימת
LOGS_DIR.mkdir(exist_ok=True)

# הגדרות הבוט
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("No Telegram token found in environment variables")

KEYWORDS = ["+40", "טיול", "יצאנו לטיול"]
LOG_FILE = LOGS_DIR / "bot_log.log"