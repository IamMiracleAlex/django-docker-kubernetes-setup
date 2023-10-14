import code

import requests
from django.utils import timezone
from numpy import empty
import pyotp
from decouple import config
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings

AFRICA_TALKING_API_KEY = config("AFRICA_TALKING_API_KEY")
AFRICA_TALKING_USERNAME = config("AFRICA_TALKING_USERNAME")
AFRICA_TALKING_ALPHA_NUM = config("AFRICA_TALKING_ALPHANUM", "AFRICASTKNG")


def generate_secret():
	return pyotp.random_base32()


def get_token(secret, interval=30):
	token = pyotp.TOTP(secret, interval=interval).now()
	return token


def make_qr_code(secret, email):
	uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name='Heckerbella DOP')
	return qr_code_img(uri)


def qr_code_img(url):
	import qrcode, base64, io
	qr = qrcode.QRCode(version=1, box_size=10, border=5)
	qr.add_data(url)
	img = qr.make_image(fill='black', back_color='white')
	img_byte_arr = io.BytesIO()
	img.save(img_byte_arr, format='PNG')
	img_byte_arr = img_byte_arr.getvalue()
	return base64.b64encode(img_byte_arr).decode()


account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')
phone_number = config('TWILIO_PHONE_NUMBER')


def send_mfa_sms(secret, number):
	if number is None or number == '':
		raise Exception('You do not have a mobile number')
	client = Client(account_sid, auth_token)
	code = get_token(secret=secret, interval=90)
	message = client.messages \
		.create(
		body=f"Your Heckerbella DOP MFA verification code is {code}.",
		from_=phone_number,
		to=number
	)
	return message.account_sid


def send_mfa_email(secret, user):
	code = get_token(secret=secret, interval=300)
	message = f"""
				Hi {user.first_name}, 
				Below is your code to login to your account.
				It expires in the next 5 minutes.

				{code}

				Thanks,
				Heckerbella Team.
				"""
	send_mail(subject="Heckerbella DOP MFA login code", message=message,
						from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email, ],
						fail_silently=True)
	return



def send_mfa_sms_(secret, number):
	header = dict(Accept="application/json")
	header["Content-Type"] = "application/x-www-form-urlencoded"
	header["apikey"] = AFRICA_TALKING_API_KEY

	code = get_token(secret=secret, interval=90)
	data = dict(username=AFRICA_TALKING_USERNAME, to=[number],
				message=f"Your Heckerbella DOP MFA verification code is {code}.")
	data["from"] = AFRICA_TALKING_ALPHA_NUM

	response = requests.post(url="https://content.africastalking.com/version1/messaging", headers=header, data=data)
	res_data = response.json()
	print(res_data)
	if res_data['SMSMessageData']['Recipients'][0]['statusCode'] not in [101, 100, 102]:
		send_mfa_sms(secret, number)
	else:
		return res_data


def send_setup_key(user):
	body = f"""
                Hello {user.first_name},

					{user.mfa_secret}

                Above is your google authenticator set up key. To set it up,
				follow the following proceedures;
				1. Open your google authenticator app
				2. click on the  +  button
				3. click on ENTER A SETUP KEY
				4. Fill in Heckerbella DOP as the account name
				5. Fill in your setup key ({user.mfa_secret}) in the your key coloumn
				6. select Time based as the type of key
				7. Click the ADD button and voila you are set up !
                
				Thank you
                """
	send_mail(subject='Heckebella DOP Google Authenticator Setup key', message=body,
			  recipient_list=[user.email, ], from_email=settings.EMAIL_HOST_USER, fail_silently=True)


def get_qr_code(user):
	secret = user.get_secret()
	return make_qr_code(secret, user.email)


def verify_g_auth(user, token):
	if not str(token).isdigit():
		return False
	secret = int(get_token(user.mfa_secret))
	if secret != int(token):
		return False
	return True


def generate_recovery_code(user):
	if not user.mfa_recovery:
		user.mfa_recovery = [pyotp.random_base32(length=32) for x in range(5)]
		user.mfa_recovery_last_generated = timezone.now()
		user.save()
	return user.mfa_recovery


def mfa_recovery_auth(user, code):
	if len(code) != 32:
		raise Exception('invalid token')
	try:
		user.mfa_recovery.remove(code)
		user.save()
		return code
	except ValueError:
		raise Exception('wrong token')
