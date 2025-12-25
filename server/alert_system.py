import smtplib
import requests
from flask_socketio import SocketIO

# Initialize WebSocket for real-time alerts
socketio = SocketIO(cors_allowed_origins="*")

# Email Configuration (Replace with your credentials)
EMAIL_SENDER = "your_email@gmail.com"  # Your Gmail ID
EMAIL_PASSWORD = "your_app_password"   # Gmail App Password (not your normal password)
EMAIL_RECIPIENT = "recipient_email@gmail.com"  # Caregiver's Email

def send_web_alert(message):
    """Sends a real-time alert message to the web page."""
    print("⚠️ ALERT:", message)
    socketio.emit("fall_alert", {"message": message})  # Send alert to web client

def send_email_alert(subject, message):
    """Sends an email alert using Gmail."""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, email_message)
        server.quit()
        print("✅ Email Alert Sent")
    except Exception as e:
        print(f"❌ Error Sending Email: {e}")

def activate_buzzer():
    """Sends a request to ESP32 to activate the buzzer alert."""
    try:
        ESP32_BUZZER_URL = "http://your_esp32_ip/buzzer"
        requests.get(ESP32_BUZZER_URL)
        print("✅ Buzzer Alert Triggered")
    except Exception as e:
        print(f"❌ Error Activating Buzzer: {e}")

def send_alert(message):
    """Triggers alert in web UI, email, and activates buzzer."""
    send_web_alert(message)  # Display alert on webpage
    send_email_alert("Fall Detection Alert", message)  # Send email
    activate_buzzer()  # Optional: Activate buzzer on ESP32
