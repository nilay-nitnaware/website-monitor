import requests
import hashlib
import json
import smtplib
import difflib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
RECIPIENT_EMAIL = "recipient-email@gmail.com"

# Load websites from file
def load_websites(file_path="websites.txt"):
    websites = {}
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(" ", 1)  # Split into name and URL
            if len(parts) == 2:
                name, url = parts
                websites[name] = url
    return websites

# Load stored hashes
def load_hashes(file_path="hashes.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save updated hashes
def save_hashes(hashes, file_path="hashes.json"):
    with open(file_path, "w") as file:
        json.dump(hashes, file, indent=4)

# Fetch website content
def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

# Compute hash of content
def compute_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

# Find differences between old and new content
def find_changes(old_content, new_content):
    diff = difflib.unified_diff(
        old_content.splitlines(), new_content.splitlines(), lineterm=""
    )
    return "\n".join(diff)

# Send email notification
def send_email(name, url, changes):
    subject = f"Website Change Alert: {name}"
    
    body = f"""
    The website '{name}' ({url}) has changed.

    Here are the changes:
    ----------------------------------------
    {changes}
    ----------------------------------------

    Check the website to see full updates.
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent: {name}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main function
def main():
    websites = load_websites()
    hashes = load_hashes()

    for name, url in websites.items():
        new_content = fetch_content(url)
        if new_content is None:
            print(f"Failed to fetch {name} ({url})")
            continue

        new_hash = compute_hash(new_content)
        old_hash = hashes.get(name)

        if old_hash and old_hash != new_hash:
            print(f"Change detected on {name} ({url})")
            old_content = fetch_content(url)  # Re-fetch to get old content
            changes = find_changes(old_content, new_content)
            send_email(name, url, changes)

        # Update the hash
        hashes[name] = new_hash

    save_hashes(hashes)

if __name__ == "__main__":
    main()
