from django.core.validators import RegexValidator
from random import randint
from kavenegar import *

def random_code(start=1000, end=9999):
    return randint(start, end)


def send_otp_code(phone_number, code):
    API_KEY = '44656A6B7A2B7A54756937704172674356557476514F7863614D4C5A5064355445584F7A71504A512B6F673D'
    try:
        api = KavenegarAPI(API_KEY)
        params = {
            'sender': '1000689696',
            'receptor': phone_number,
            'message': f'{code} :کد تایید شما -Deja'
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)

phone_regex = r'^(\+989|09)+\d{9}$'

phone_regex_validator = RegexValidator(
    regex=phone_regex, message="Invalid Phone number. Phone number must be like: +989XXXXXXXXX or 09XXXXXXXXX"
)

full_name_regex = r'(^[A-Za-z]{3,16})([ ]{0,1})([A-Za-z]{3,16})?([ ]{0,1})?([A-Za-z]{3,16})$'

full_name_regex_validator = RegexValidator(
    regex=full_name_regex,
    message="Invalid Full name. Full name must only contain alphabet letters and whitespace."
)