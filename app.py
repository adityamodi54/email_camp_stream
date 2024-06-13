import streamlit as st
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

from_email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

if not from_email or not password:
    st.error("Please set EMAIL and PASSWORD environment variables")

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"Failed to send email to {to_email}: {e}"

def main():
    st.title("Email Campaign App")

    st.header("Send Emails")
    email_addresses = st.text_area("Enter email addresses (separated by commas)")
    subject = st.text_input("Email Subject")
    body = st.text_area("Email Body")

    if st.button("Send Emails"):
        if email_addresses and subject and body:
            emails = email_addresses.split(',')
            results = []
            for email_id in emails:
                result = send_email(email_id.strip(), subject, body)
                results.append(result)
            for result in results:
                st.write(result)
        else:
            st.error("Please fill out all fields")

if __name__ == "__main__":
    main()
