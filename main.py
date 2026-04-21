import os
import boto3
import config
from scraper import get_jobs
from telegram_bot import send_message

# We use os.getenv('AWS_REGION') so it automatically looks in the exact region where Lambda is running
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'eu-central-1')) 
table = dynamodb.Table(config.DYNAMODB_TABLE)

def load_seen_jobs():
    """Fetches all previously seen job IDs from the DynamoDB table."""
    try:
        response = table.scan(ProjectionExpression="job_id")
        return {item['job_id'] for item in response.get('Items', [])}
    except Exception as e:
        print(f"Error reading DB: {e}")
        return set()

def lambda_handler(event, context):
    print("Starting job scan...")
    seen_job_ids = load_seen_jobs()
    current_jobs = get_jobs()
    
    # 1. Filter out jobs we have already seen
    new_jobs = [job for job in current_jobs if job["id"] not in seen_job_ids]
    print(f"Found {len(current_jobs)} total jobs on page. {len(new_jobs)} are new.")
    
    # If there are no new jobs, exit gracefully without sending a message
    if not new_jobs:
        msg = "Finished! No new jobs to report."
        print(msg)
        return {'statusCode': 200, 'body': msg}

    # 2. Build a single, consolidated Telegram message
    message = f"🚨 <b>Found {len(new_jobs)} New Jobs!</b> 🚨\n\n"
    for job in new_jobs:
        message += f"▪️ <b>{job['title']}</b> at {job['company']}\n<a href='{job['link']}'>Apply Here</a>\n\n"

    # 3. Send the master message
    if send_message(message):
        # 4. Save the new jobs to DynamoDB in one efficient batch
        try:
            with table.batch_writer() as batch:
                for job in new_jobs:
                    batch.put_item(Item={'job_id': str(job["id"])})
            print(f"Successfully saved {len(new_jobs)} new jobs to DynamoDB.")
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
            
    msg = f"Finished! Sent 1 consolidated alert for {len(new_jobs)} jobs."
    print(msg)
    return {'statusCode': 200, 'body': msg}

if __name__ == "__main__":
    lambda_handler(None, None)