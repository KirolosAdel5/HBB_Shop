import random
from twilio.rest import Client
from django.conf import settings

def generate_otp(length=6):
    """
    Generate a random numeric OTP of the specified length (default is 6 digits).
    """
    digits = "0123456789"
    otp = "".join(random.choice(digits) for _ in range(length))
    return otp


def send_otp_via_sms(phone_number, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f'Your OTP code is: {otp}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to="+201289022985"
    )
    return message.sid