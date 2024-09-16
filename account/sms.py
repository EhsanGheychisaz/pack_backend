import requests
import secrets
from .models import SMSComfirmCode, User


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
