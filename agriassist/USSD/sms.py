from django.conf import settings
import africastalking

africastalking.initialize(
    settings.AFRICAS_TALKING_USERNAME,
    settings.AFRICAS_TALKING_API_KEY,
)

sms = africastalking.SMS

def send_sms(phone_number: str, message: str) -> None:
    sms.send(
        message = message,
        receipient = [phone_number],
    )