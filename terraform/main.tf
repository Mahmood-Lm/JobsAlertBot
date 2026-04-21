provider "aws" {
  region = var.aws_region
}

# 1. DynamoDB Table
resource "aws_dynamodb_table" "jobs_table" {
  name         = "LinkedInJobs"
  billing_mode = "PAY_PER_REQUEST" # Free tier friendly
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }
}

# 2. ECR Repository
resource "aws_ecr_repository" "bot_repo" {
  name                 = "linkedin-job-bot"
  force_delete         = true # Allows TF to delete the repo even if it contains images
}

# 3. IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "linkedin_bot_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# 4. IAM Policy: Allow Lambda to write to DynamoDB and CloudWatch Logs
resource "aws_iam_role_policy" "lambda_policy" {
  name = "linkedin_bot_lambda_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.jobs_table.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# 5. The Lambda Function
resource "aws_lambda_function" "bot_lambda" {
  function_name = "linkedin-job-bot-function"
  role          = aws_iam_role.lambda_exec_role.arn
  
  # Tells AWS we are using a Docker container
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.bot_repo.repository_url}:latest"

  memory_size = 1024
  timeout     = 60

  environment {
    variables = {
      TELEGRAM_TOKEN = var.telegram_token
      CHAT_ID        = var.chat_id
      DYNAMODB_TABLE = aws_dynamodb_table.jobs_table.name
    }
  }

  # This ensures Lambda waits for the IAM policy to be attached first
  depends_on = [aws_iam_role_policy.lambda_policy]
}

# 6. EventBridge Schedule (Run every 1 hour from 7 AM to 9 PM CET / 5 AM to 7 PM UTC)
resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "every-hour-cet"
  schedule_expression = "cron(0 5-19 * * ? *)"
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "TriggerLinkedInBot"
  arn       = aws_lambda_function.bot_lambda.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.bot_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule.arn
}

# Output the repository URL so we know where to push the Docker image
output "ecr_repository_url" {
  value = aws_ecr_repository.bot_repo.repository_url
}

# Attach AWS managed policy for DynamoDB full access 
resource "aws_iam_role_policy_attachment" "dynamodb_full_access" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}