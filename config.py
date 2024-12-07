import os
from pathlib import Path
from dotenv import load_dotenv

# טעינת משתני הסביבה - חשוב במיוחד בסביבת Render
load_dotenv()

# הגדרת נתיבי בסיס
# בסביבת Render, אנחנו צריכים להשתמש בנתיבים יחסיים לתיקיית הפרויקט
BASE_DIR = Path(__file__).parent

# הגדרת נתיבים לקבצי המערכת
# אנחנו משתמשים ב-os.getenv כדי לאפשר גמישות בין סביבות שונות
LOGS_DIR = Path(os.getenv('LOG_DIR', BASE_DIR / "logs"))
DATA_FILE = Path(os.getenv('DATA_FILE', BASE_DIR / "dog_walks_data.json"))

# וידוא שתיקיית הלוגים קיימת
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create logs directory: {e}")
    # אם לא מצליחים ליצור את התיקייה, נשתמש בתיקייה הנוכחית
    LOGS_DIR = BASE_DIR

# הגדרות הבוט
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("No Telegram token found in environment variables")

# הגדרת מילות המפתח לזיהוי טיולים
KEYWORDS = ["+40", "טיול", "יצאנו לטיול"]

# הגדרת קובץ הלוג
LOG_FILE = LOGS_DIR / "bot_log.log"