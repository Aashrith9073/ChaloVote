from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

def send_notification(contact_info: str, message: str, subject: str = "Your new trip awaits!"):
    """
    Determines whether to send an SMS or Email based on the contact_info.
    """
    if "@" in contact_info:
        # It's an email
        send_email(to_email=contact_info, subject=subject, html_content=message)
    else:
        # Assume it's a phone number
        send_sms(to_number=contact_info, body=message)

def send_sms(to_number: str, body: str):
    """
    Sends an SMS using Twilio.
    """
    # Only try to send if the credentials are set
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            print(f"SMS sent to {to_number}. SID: {message.sid}")
        except Exception as e:
            print(f"Error sending SMS to {to_number}: {e}")
    else:
        print("--- SKIPPING SMS: Twilio credentials not found. ---")
        print(f"TO: {to_number}\nBODY: {body}")

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using SendGrid.
    """
    # Only try to send if the credentials are set
    if settings.SENDGRID_API_KEY and settings.SENDER_EMAIL:
        message = Mail(
            from_email=settings.SENDER_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"Email sent to {to_email}. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
    else:
        print("--- SKIPPING EMAIL: SendGrid credentials not found. ---")
        print(f"TO: {to_email}\nSUBJECT: {subject}\nBODY: {html_content}")