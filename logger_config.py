import logging
from logging.handlers import RotatingFileHandler
from config import LOG_FILE

def setup_logger(name: str = None) -> logging.Logger:
    """
    הגדרת מערכת לוגים מתקדמת
    
    Args:
        name (str, optional): שם הלוגר. ברירת המחדל היא None
    
    Returns:
        logging.Logger: אובייקט הלוגר המוגדר
    """
    # יצירת לוגר
    logger = logging.getLogger(name or __name__)
    logger.setLevel(logging.INFO)
    
    # בדיקה אם כבר יש handlers ללוגר
    if not logger.handlers:
        # הגדרת פורמט
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # הגדרת handler לקובץ
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # הגדרת handler לקונסול
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # הוספת handlers ללוגר
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger