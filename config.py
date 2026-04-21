import os
from dotenv import load_dotenv

# This loads the local .env file if it exists (for local laptop testing)
load_dotenv() 

# Fetch the secrets and settings from the environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# We use getenv for the table with a fallback default name / works both locally and in AWS Lambda where we set the env variable via Terraform
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "LinkedInJobs") 

# LinkedIn search URL
SEARCH_URL = "https://www.linkedin.com/jobs/search?keywords=Devops&location=Rome&geoId=106398949&f_TPR=r86400&position=1&pageNum=0"
# SEEN_JOBS_FILE = "seen_jobs.txt"