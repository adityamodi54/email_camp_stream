import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Load environment variables from .env file if it exists
load_dotenv()

from_email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

if not from_email or not password:
    st.error("Please set EMAIL and PASSWORD environment variables")

# Follow-up messages
follow_up_messages = [
    "This is the first follow-up message.",
    "This is the second follow-up message.",
    "This is the third follow-up message."
]

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()

# Function to send an email
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

# Function to schedule follow-up emails
def schedule_follow_ups(to_email):
    for i, follow_up_body in enumerate(follow_up_messages):
        subject = f"Follow-up {i+1}"
        run_date = datetime.now() + timedelta(days=i+1)
        scheduler.add_job(send_email, 'date', run_date=run_date, args=[to_email, subject, follow_up_body])

def main():
    st.title("Email Campaign App")

    st.header("Send Emails")
    email_addresses = st.text_area("Enter email addresses (separated by commas)")
    initial_subject = st.text_input("Initial Email Subject")
    initial_body = st.text_area("Initial Email Body")

    if st.button("Send Initial Emails"):
        if email_addresses and initial_subject and initial_body:
            emails = email_addresses.split(',')
            results = []
            for email_id in emails:
                result = send_email(email_id.strip(), initial_subject, initial_body)
                results.append(result)
            for result in results:
                st.write(result)

            # Schedule follow-ups
            for email_id in emails:
                schedule_follow_ups(email_id.strip())
        else:
            st.error("Please fill out all fields")

if __name__ == "__main__":
    main()
