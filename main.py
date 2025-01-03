import json
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import schedule
from dotenv import load_dotenv
from loguru import logger
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv(dotenv_path='.env')

# Instagram credentials
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Email settings
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")

# Script settings
ACCOUNTS_TO_WATCH = [
    "troonbrewing",
    # Add more accounts here
]
MAX_POSTS_TO_CHECK = 5
COOKIE_BUTTON_SELECTOR = 'button._a9--._ap36._a9_1'


def load_known_posts():
    try:
        with open('known_posts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Dictionary to store posts by account


def save_known_posts(posts):
    with open('known_posts.json', 'w') as f:
        json.dump(posts, f)


def send_email(subject, body):
    # Email configuration
    sender_name = "Instagram Account Notifier"
    sender_email = GMAIL_ADDRESS
    sender_password = GMAIL_APP_PASSWORD
    receiver_email = NOTIFICATION_EMAIL

    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"  # Proper email format with display name
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        logger.success("Email notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")


def scrape_instagram(accounts_to_watch=ACCOUNTS_TO_WATCH):
    known_posts = load_known_posts()
    all_new_posts = []  # Track all new posts across accounts

    # Initialize accounts that haven't been tracked before
    for account in accounts_to_watch:
        if account not in known_posts:
            known_posts[account] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Login to Instagram
            logger.info("Logging into Instagram...")
            page.goto('https://www.instagram.com/accounts/login/')
            time.sleep(2)

            # Handle cookies popup
            try:
                if page.locator(COOKIE_BUTTON_SELECTOR).count() > 0:
                    page.click(COOKIE_BUTTON_SELECTOR)
                    logger.info("Handled cookie popup")
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"Cookie handling error (continuing anyway): {str(e)}")

            # Login
            page.fill('input[name="username"]', USERNAME)
            page.fill('input[name="password"]', PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            for account in accounts_to_watch:
                logger.info(f"Checking account: {account}")
                new_posts = []

                # Navigate to account page
                page.goto(f'https://www.instagram.com/{account}/')
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                # Handle age verification if needed
                if page.locator('text="Yes, I\'m 21 or Older"').count() > 0:
                    page.click('text="Yes, I\'m 21 or Older"')
                    time.sleep(2)

                # Get recent posts
                posts = page.locator('a[href*="/p/"]').all()

                for post in posts[:MAX_POSTS_TO_CHECK]:
                    href = post.get_attribute('href')
                    post_id = href.split('/p/')[1].strip('/')

                    if post_id not in known_posts[account]:
                        img = post.locator('img').first
                        alt_text = img.get_attribute('alt') if img else "No caption"

                        # Store new post info
                        all_new_posts.append({
                            'account': account,
                            'post_id': post_id,
                            'caption': alt_text
                        })

                        logger.info("=" * 50)
                        logger.info(f"New post found! ID: {post_id}")
                        logger.info(f"Caption: {alt_text}")
                        new_posts.append(post_id)

                if not new_posts:
                    logger.info(f"No new posts found for {account}")
                else:
                    logger.success(f"Found {len(new_posts)} new posts for {account}")

                # Update known posts for this account
                known_posts[account].extend(new_posts)

            # Send one email for all new posts
            if all_new_posts:
                subject = f"New Instagram Posts Found ({len(all_new_posts)} posts)"
                body = "New posts detected:\n\n"

                for post in all_new_posts:
                    body += f"""
Account: {post['account']}
Post ID: {post['post_id']}
Caption: {post['caption']}
Link: https://instagram.com/p/{post['post_id']}/
{'=' * 40}
"""
                send_email(subject, body)

            # Save all updates
            save_known_posts(known_posts)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
        finally:
            browser.close()


if __name__ == "__main__":
    logger.info("Starting Instagram post checker...")

    # Schedule the job
    schedule.every(15).minutes.do(scrape_instagram)

    # Run immediately on startup
    scrape_instagram()

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)
