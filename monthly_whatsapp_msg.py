import streamlit as st
import pandas as pd
import datetime
import pywhatkit as kit
import time
import calendar
import os

# File to store reminders
DATA_FILE = "reminders.csv"

# Load or create reminder data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Phone", "Day", "Message"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Adjust date if it's weekend
def get_next_reminder_day(day):
    today = datetime.date.today()
    year = today.year
    month = today.month
    try:
        reminder_date = datetime.date(year, month, int(day))
    except ValueError:
        last_day = calendar.monthrange(year, month)[1]
        reminder_date = datetime.date(year, month, last_day)

    if reminder_date.weekday() == 5:  # Saturday
        reminder_date += datetime.timedelta(days=2)
    elif reminder_date.weekday() == 6:  # Sunday
        reminder_date += datetime.timedelta(days=1)

    return reminder_date

# Send WhatsApp Message
def send_whatsapp_message(phone, message):
    phone = str(phone)  # 💡 Convert phone to string
    if not phone.startswith("+"):
        phone = "+" + phone  # 💡 Ensure country code is included
    now = datetime.datetime.now()
    send_time = now + datetime.timedelta(minutes=2)
    hour = send_time.hour
    minute = send_time.minute
    st.info(f"Scheduling message to {phone} at {hour}:{minute:02d}")
    kit.sendwhatmsg(phone, message, hour, minute)
    time.sleep(10)
# Streamlit UI
st.set_page_config(page_title="WhatsApp Reminder Scheduler", layout="centered")

st.title("📱 WhatsApp Monthly Reminder Scheduler")

df = load_data()

# Add reminder section
with st.form("add_reminder"):
    st.subheader("➕ Add New Reminder")
    name = st.text_input("Name")
    phone = st.text_input("Phone Number (with country code)", value="+91")
    day = st.number_input("Day of the Month", min_value=1, max_value=31)
    message = st.text_area("Reminder Message")
    submitted = st.form_submit_button("Add Reminder")

    if submitted and name and phone and message:
        new_row = pd.DataFrame([[name, phone, day, message]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("Reminder added successfully!")

# Display current reminders
st.subheader("📋 Existing Reminders")
if df.empty:
    st.info("No reminders yet.")
else:
    st.dataframe(df)

# Check and send today's reminders
if st.button("📤 Check and Send Today's Reminders"):
    today = datetime.date.today()
    sent_any = False
    for index, row in df.iterrows():
        due_date = get_next_reminder_day(row["Day"])
        if today == due_date:
            send_whatsapp_message(row["Phone"], row["Message"])
            sent_any = True
    if not sent_any:
        st.info("No reminders to send today.")

