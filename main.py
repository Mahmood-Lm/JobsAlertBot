import time
import boto3
import config
from scraper import get_jobs
from telegram_bot import send_message

# Initialize the connection to AWS DynamoDB
# We specify the region we set in Terraform to be safe
dynamodb = boto3.resource('dynamodb', region_name='eu-south-1') 
table = dynamodb.Table(config.DYNAMODB_TABLE)

def load_seen_jobs():
    """Fetches all previously seen job IDs from the DynamoDB table."""
    try:
        response = table.scan(ProjectionExpression="job_id")
        return {item['job_id'] for item in response.get('Items', [])}
    except Exception as e:
        print(f"Error reading from DynamoDB: {e}")
        return set()

def save_seen_job(job_id):
    """Saves a newly found job ID to the DynamoDB table."""
    try:
        table.put_item(Item={'job_id': str(job_id)})
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")

def lambda_handler(event, context):
    """
    This is the entry point that AWS Lambda calls when triggered by EventBridge.
    The 'event' and 'context' parameters are required by AWS, even if we don't use them.
    """
    print("Starting Serverless job scan...")
    
    # 1. Get history from DynamoDB
    seen_job_ids = load_seen_jobs()
    
    # 2. Scrape current jobs via Playwright
    current_jobs = get_jobs()
    print(f"Found {len(current_jobs)} jobs on the page.")
    
    new_jobs_count = 0
    
    # 3. Compare and alert
    for job in current_jobs:
        if job["id"] not in seen_job_ids:
            message = f"🚨 <b>New Job Alert</b> 🚨\n\n<b>Role:</b> {job['title']}\n<b>Company:</b> {job['company']}\n\n<a href='{job['link']}'>Apply Here</a>"
            
            if send_message(message):
                save_seen_job(job["id"])
                new_jobs_count += 1
                time.sleep(1) # Prevent hitting Telegram's rate limit

    result_message = f"Finished! Sent {new_jobs_count} new job alerts."
    print(result_message)
    
    # AWS Lambda expects a return response, usually a status code
    return {
        'statusCode': 200,
        'body': result_message
    }

# This bottom block allows you to still test the code manually by running `python main.py` on your PC
if __name__ == "__main__":
    # We pass None for event and context since we aren't triggering it from AWS locally
    lambda_handler(None, None)