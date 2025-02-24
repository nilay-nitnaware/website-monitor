import os
import hashlib
import requests
import smtplib
from email.mime.text import MIMEText

# Website URL to monitor
URL = "https://example.com"  # Replace with the actual website URL

# Email credentials stored in GitHub Secrets
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Function to send an email
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to get the hash of the website content
def get_page_hash(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        page_content = response.text
        return hashlib.sha256(page_content.encode()).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

# Check for changes
previous_hash = None
current_hash = get_page_hash(URL)

if current_hash and previous_hash and current_hash != previous_hash:
    send_email("Website Change Detected", f"The content of {URL} has changed.")
previous_hash = current_hash
