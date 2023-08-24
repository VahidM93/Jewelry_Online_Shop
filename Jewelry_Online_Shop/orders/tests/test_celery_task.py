from django.test import TestCase
from orders.tasks import send_order_status_email
from unittest import mock


class SendOrderStatusEmailTestCase(TestCase):
    @mock.patch("orders.tasks.send_mail")
    def test_send_order_status_email_success(self, mock_send_mail):
        # Mock the send_mail function to avoid actual email sending
        instance = mock_send_mail.return_value
        # Call the Celery task
        result = send_order_status_email.delay(
            "test@example.com", "Test message", "Test subject"
        )
        self.assertEqual(result.get(), "Email sent to test@example.com successfully")