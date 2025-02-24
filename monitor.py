import os
import hashlib
import requests
import smtplib
from email.mime.text import MIMEText

# Email credentials stored in GitHub Secrets
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# File containing website list
WEBSITE_FILE = "websites.txt"

# Dictionary to store previous hashes
previous_hashes = {}

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
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to get the hash of the website content
def get_page_hash(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return hashlib.sha256(response.text.encode()).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Read websites from file
if os.path.exists(WEBSITE_FILE):
    with open(WEBSITE_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                name, url = parts
                current_hash = get_page_hash(url)

                if url in previous_hashes and current_hash and previous_hashes[url] != current_hash:
                    send_email(f"Website Change Detected: {name}", f"The content of {name} ({url}) has changed.")

                previous_hashes[url] = current_hash
else:
    print(f"Error: {WEBSITE_FILE} not found!")
