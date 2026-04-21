# 🚀 Serverless LinkedIn Job Bot

An automated, serverless Python bot that scrapes public LinkedIn job postings and sends real-time alerts to a Telegram chat. Built with Playwright and fully deployed on AWS (Lambda, DynamoDB, ECR) using Terraform and GitHub Actions.



## 🏗️ Project Architecture
* **Scraping:** Python + Playwright (Headless Chromium)
* **Infrastructure as Code:** Terraform
* **CI/CD Pipeline:** GitHub Actions
* **Cloud Provider:** AWS (EventBridge, Lambda, ECR, DynamoDB)
* **Notifications:** Telegram Bot API