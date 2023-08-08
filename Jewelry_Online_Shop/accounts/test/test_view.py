from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from accounts.views import OtpCode

User = get_user_model()

class AuthenticationViewTests(TestCase):
    def setUp(self):
        # Set up any necessary data for the tests
        self.user_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'password': 'testpassword',
        }

    def test_user_registration_view(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_user_verification_view(self):
        # Create an OTP code for the user
        otp_code = OtpCode.objects.create(phone_number=self.user_data['phone'], code='123456')
        session_data = {
            'user_registration_info': {
                'phone_number': self.user_data['phone'],
                'email': self.user_data['email'],
                'full_name': self.user_data['full_name'],
                'password': self.user_data['password'],
            }
        }
        self.client.session['user_registration_info'] = session_data
        response = self.client.get(reverse('accounts:verify_code'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_view(self):
        # Create a user for testing
        user = User.objects.create_user(
            phone_number=self.user_data['phone'],
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_user_logout_view(self):
        self.client.force_login(User.objects.create_user(phone_number='1234567890', password='testpassword'))
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product:home'))


    def test_invalid_login(self):
        response = self.client.post(reverse('accounts:login'), data={
            'phone': self.user_data['phone'],
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Phone number or Password is WRONG!')

    def test_valid_login(self):
        user = User.objects.create_user(
            phone_number=self.user_data['phone'],
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        response = self.client.post(reverse('accounts:login'), data={
            'phone': self.user_data['phone'],
            'password': self.user_data['password'],
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product:home'))

        # Make sure the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
