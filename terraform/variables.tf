variable "aws_region" {
  description = "The AWS region to deploy in"
  default     = "eu-central-1"
}

variable "telegram_token" {
  description = "Telegram Bot Token"
  type        = string
  sensitive   = true
}

variable "chat_id" {
  description = "Telegram Chat ID"
  type        = string
  sensitive   = true
}