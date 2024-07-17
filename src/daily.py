import logging
import time
from datetime import datetime
import schedule
from etl import extract

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def daily_job():
    logging.info(f"Running daily job at {datetime.now()}")
    extract()

def schedule_daily_job():
    # Schedule the job to run daily at midnight
    schedule.every().day.at("00:00").do(daily_job)

    logging.info(f"Schedules: {schedule.get_jobs()}")
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.error(e)
            
        time.sleep(1)

if __name__ == "__main__":
    schedule_daily_job()