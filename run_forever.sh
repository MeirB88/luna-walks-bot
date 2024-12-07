#!/bin/bash

# הגדרת הנתיב לקובץ הלוג
LOG_FILE="/home/meirb/luna_walks_bot/nohup.out"

# פונקציה לכתיבת לוג
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# רישום התחלת הריצה
log_message "Starting bot script"

# לולאה אינסופית
while true; do
    log_message "Attempting to start the bot"
    
    # הרצת הבוט עם לוגים של שגיאות
    /home/meirb/.local/bin/python3 /home/meirb/luna_walks_bot/bot.py 2>> "$LOG_FILE"
    
    # רישום סיום הריצה
    log_message "Bot stopped or crashed, waiting 5 seconds before restart"
    
    # המתנה לפני הרצה מחדש
    sleep 5
done
