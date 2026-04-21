# config.py
import os
from dotenv import load_dotenv

# This function looks for the .env file and loads the variables into the environment
load_dotenv() 

# Fetch the secrets safely
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Non-sensitive settings
SEARCH_URL = "https://www.linkedin.com/jobs/search?keywords=Devops&location=Rome&geoId=106398949&f_TPR=r86400&position=1&pageNum=0"
SEEN_JOBS_FILE = "seen_jobs.txt"