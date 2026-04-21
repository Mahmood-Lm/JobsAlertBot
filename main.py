# main.py
import os
import time
import config
from scraper import get_jobs
from telegram_bot import send_message

def load_seen_jobs():
    if not os.path.exists(config.SEEN_JOBS_FILE):
        return set()
    with open(config.SEEN_JOBS_FILE, "r") as f:
        return set(f.read().splitlines())

def save_seen_job(job_id):
    with open(config.SEEN_JOBS_FILE, "a") as f:
        f.write(job_id + "\n")

def main():
    print("Starting job scan...")
    seen_job_ids = load_seen_jobs()
    current_jobs = get_jobs()
    
    print(f"Found {len(current_jobs)} jobs on the page.")

    new_jobs_count = 0
    
    for job in current_jobs:
        if job["id"] not in seen_job_ids:
            # Format the message
            message = f"🚨 <b>New Job Alert</b> 🚨\n\n<b>Role:</b> {job['title']}\n<b>Company:</b> {job['company']}\n\n<a href='{job['link']}'>Apply Here</a>"
            
            # Send it
            if send_message(message):
                save_seen_job(job["id"])
                new_jobs_count += 1
                time.sleep(1) # Prevent Telegram rate limits

    print(f"Finished! Sent {new_jobs_count} new job alerts.")

if __name__ == "__main__":
    main()