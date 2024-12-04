import pyotp
from twilio.rest import Client
from .models import SMSComfirmCode, User, SecretKeyUser
import secrets

# Set up Twilio client with your Twilio credentials
TWILIO_ACCOUNT_SID = 'AC0c77a1e6b54b2b38cef5e9b9831b9e3c'  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = 'aa3514a377678f425efaffb1b37d92ae'  # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = '+14173612699'  # Replace with your Twilio phone number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def format_phone_number(phone_number: str, country_code: str) -> str:
    """
    Format the phone number in E.164 format by adding the correct country code.
    """
    # Ensure the phone number does not have spaces or dashes
    phone_number = phone_number.replace(" ", "").replace("-", "")

    # Check the country code and format the number accordingly
    if country_code == "IR":  # Iran
        return f"+98{phone_number[1:]}"  # Remove the leading '0' for Iran numbers
    elif country_code == "AE":  # UAE
        return f"+971{phone_number[1:]}"  # Remove the leading '0' for UAE numbers
    else:
        # For other countries, assume the number is already in E.164 format
        if not phone_number.startswith('+'):
            raise ValueError("Phone number must start with a '+' and the country code")
        return phone_number


def send_sms(to_number: str, message_body: str):
    """
    Send SMS using Twilio to the given phone number.
    """
    # Ensure the phone number is in correct E.164 format
    if not to_number.startswith('+'):
        raise ValueError("Phone number must start with '+' followed by the country code")

    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number  # Ensure 'to' is a valid number
        )
        print(f"Message sent successfully with SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send message: {e}")


# Example usage for sending a confirmation code
def generateConfirmCode(user):
    """
    Generates and sends a 4-digit confirmation code to the user's phone number via SMS.
    """
    # Generate a 4-digit confirmation code
    code = 0
    while (code < 1000 or code > 9999):
        code = secrets.randbits(20) % 10000  # Ensure the code is 4 digits

    # Ensure the user's phone number is in E.164 format
    formatted_phone_number = format_phone_number(user.phone, "AE")

    # Send the confirmation code via SMS using Twilio
    try:
        message = client.messages.create(
            body=f"Your confirmation code is {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=formatted_phone_number
        )

        # Check if the message was successfully sent
        if message.sid:
            # Store the confirmation code in the database
            SMSComfirmCode.objects.create(code=code, user=user)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False


def generateTotpCode(phone):
    """
    Generates a TOTP code and sends it to the user's phone number via SMS.
    """
    # Fetch the user using the phone number
    try:
        user = User.objects.filter(phone=phone).get()
    except User.DoesNotExist:
        print(f"User with phone {phone} not found")
        return False

    # Fetch the secret key for the user
    try:
        secret_key_user = SecretKeyUser.objects.filter(user_id=user.id).get()
        secret_key = secret_key_user.key  # Extract the secret key
    except SecretKeyUser.DoesNotExist:
        print(f"Secret key not found for user {user.id}")
        return False

    # Generate the TOTP code using pyotp
    totp = pyotp.TOTP(secret_key, interval=300, digits=6)
    code = totp.now()

    # Append the user ID to the code for uniqueness (as in the original code)
    code = f"{code}{user.id}"

    # Ensure the user's phone number is in E.164 format
    formatted_phone_number = format_phone_number(user.phone, user.country_code)

    # Send the TOTP code via SMS using Twilio
    try:
        message = client.messages.create(
            body=f"Your TOTP code is {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=formatted_phone_number
        )

        if message.sid:
            # Store the confirmation code in the database
            SMSComfirmCode.objects.create(code=code, user=user)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False
