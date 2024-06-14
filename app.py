import streamlit as st
import smtplib
import logging
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to load email credentials
def load_credentials():
    from_email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    
    # If environment variables are not set, try to load from Streamlit secrets
    if not from_email or not password:
        try:
            from_email = st.secrets["email"]["EMAIL"]
            password = st.secrets["email"]["PASSWORD"]
            logger.info("Loaded email credentials from Streamlit secrets")
        except Exception as e:
            st.error("Please set EMAIL and PASSWORD environment variables or in Streamlit secrets")
            st.stop()
    
    if not from_email or not password:
        st.error("Please set EMAIL and PASSWORD environment variables")
        st.stop()
    
    return from_email, password

# Load environment variables from .env file if it exists
load_dotenv()
from_email, password = load_credentials()

# Follow-up messages
follow_up_messages = [
    "This is the first follow-up message.",
    "This is the second follow-up message.",
    "This is the third follow-up message."
]

# Dictionary to store scheduled follow-up times
scheduled_follow_ups = {}

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
        logger.info(f"Email sent to {to_email}")
        print(f"Email sent to {to_email}")
        return f"Email sent to {to_email}"
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        print(f"Failed to send email to {to_email}: {e}")
        return f"Failed to send email to {to_email}: {e}"

# Function to schedule follow-up emails using threading
def schedule_follow_ups(to_email):
    if to_email not in scheduled_follow_ups:
        scheduled_follow_ups[to_email] = []

    def schedule_email(delay, subject, body):
        time.sleep(delay)
        send_email(to_email, subject, body)
        # Remove the sent follow-up time from the dictionary
        scheduled_follow_ups[to_email].pop(0)

    for i, follow_up_body in enumerate(follow_up_messages):
        subject = f"Follow-up {i+1}"
        delay = (i + 1) * 300  # 300 seconds = 5 minutes
        follow_up_time = datetime.now() + timedelta(seconds=delay)
        threading.Thread(target=schedule_email, args=(delay, subject, follow_up_body)).start()
        scheduled_follow_ups[to_email].append(follow_up_time)
        logger.info(f"Scheduled follow-up {i+1} for {to_email} at {follow_up_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scheduled follow-up {i+1} for {to_email} at {follow_up_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"Scheduled follow-up {i+1} for {to_email} at {follow_up_time.strftime('%Y-%m-%d %H:%M:%S')}")

def format_timedelta(timedelta):
    seconds = int(timedelta.total_seconds())
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"

def main():
    st.title("Adi's Email Campaign App")

    st.header("Send Emails")
    email_addresses = st.text_area("Enter email addresses (separated by commas)")
    initial_subject = st.text_input("Initial Email Subject")
    initial_body = st.text_area("Initial Email Body")

    if st.button("Send Emails"):
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
                st.write(f"Follow-up emails for {email_id.strip()} scheduled.")
        else:
            st.error("Please fill out all fields")

    st.header("Check Next Follow-up Time")
    email_to_check = st.text_input("Enter email address to check next follow-up time")
    if st.button("Check Next Follow-up"):
        if email_to_check in scheduled_follow_ups and scheduled_follow_ups[email_to_check]:
            next_follow_up_time = scheduled_follow_ups[email_to_check][0]
            time_left = next_follow_up_time - datetime.now()
            st.write(f"Next follow-up time for {email_to_check.strip()} is at {next_follow_up_time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"Time left: {format_timedelta(time_left)}")
            print(f"Next follow-up time for {email_to_check.strip()} is at {next_follow_up_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Time left: {format_timedelta(time_left)}")
        else:
            st.write(f"No scheduled follow-ups for {email_to_check.strip()}")
            print(f"No scheduled follow-ups for {email_to_check.strip()}")

if __name__ == "__main__":
    main()
