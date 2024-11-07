import requests
import secrets
from .models import SMSComfirmCode, User,SecretKeyUser

import pyotp
def generateConfirmCode(user):
    code = 0
    while (code < 1000 or code > 9999):
        code = secrets.randbits(20)
        # print(code)

    # print(code)
    # print(user.phone) 

    data = {
        "bodyId": 171434,
        "to": user.phone,
        "args": [user.phone, str(code)]
    }

    response = requests.post(
        'https://console.melipayamak.com/api/send/shared/c7feee33bdc0455f88224c2dedded715', json=data)

    print(response.json())

    if response.json()['status'] == 'ارسال موفق بود':
        SMSComfirmCode.objects.create(code=code, user=user)
        return True
    else:
        return False


# generateConfirmCode()

def generateTotpُCode(phone):

    # Ensure totp_code is long enough to contain code and user_id


    # Fetch the user using the user_id
    user = User.objects.filter(phone=phone).get()
    # Fetch the secret key from the SecretKeyUser model
    secret_key_user = SecretKeyUser.objects.filter(user_id=user.id).get()
    secret_key = secret_key_user.key  # Extract the secret key

    # Generate the TOTP object with the retrieved secret_key and 120-second interval
    totp = pyotp.TOTP(secret_key, interval=300, digits=6)

    # Verify the TOTP code with a valid window of 1
    code =  totp.now()
    code = code + f"{user.id}"
    data = {
        "bodyId": 171434,
        "to": user.phone,
        "args": [user.phone, str(code)]
    }

    response = requests.post(
        'https://console.melipayamak.com/api/send/shared/c7feee33bdc0455f88224c2dedded715', json=data)


    if response.json()['status'] == 'ارسال موفق بود':
        SMSComfirmCode.objects.create(code=code, user=user)
        return True
    else:
        return False
