# scraper.py
from playwright.sync_api import sync_playwright
import time
import config

def get_jobs():
    jobs_found = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage", # AWS Lambda has very limited shared memory
                "--disable-gpu",           # AWS Lambda has no GPU
                "--single-process",        # Forces browser into one thread to avoid Lambda process limits
                "--no-zygote"              # Disables a specific process fork that Lambda blocks
            ]
        )        
        
        page = browser.new_page()
        
        print("Navigating to LinkedIn...")
        page.goto(config.SEARCH_URL)
        time.sleep(3) # Wait for jobs to load
        
        job_cards = page.locator('ul.jobs-search__results-list > li').all()
        
        for card in job_cards:
            try:
                title = card.locator('h3.base-search-card__title').inner_text().strip()
                company = card.locator('h4.base-search-card__subtitle').inner_text().strip()
                link = card.locator('a.base-card__full-link').get_attribute('href')
                
                clean_link = link.split('?')[0] 
                job_id = clean_link.split('-')[-1]
                
                jobs_found.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "link": clean_link
                })
            except Exception:
                continue 
                
        browser.close()
        
    return jobs_found