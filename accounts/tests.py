from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration(self):
        payload = {
            'username': 'newrider',
            'first_name': 'New',
            'last_name': 'Rider',
            'email': 'newrider@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        }
        res = self.client.post(reverse('accounts:register'), payload)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='newrider').exists())

    def test_login_and_dashboard(self):
        User.objects.create_user(username='rider1', email='r1@example.com', password='mypassword123')
        res_login = self.client.post(reverse('accounts:login'), {'username': 'rider1', 'password': 'mypassword123'})
        self.assertEqual(res_login.status_code, 302)

        res_dash = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, "Account Dashboard")

    def test_password_reset_unregistered_email_rejected(self):
        res = self.client.post(reverse('accounts:password_reset'), {'email': 'unknown@example.com'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "No active account found with this email address")

    def test_password_reset_registered_email_accepted(self):
        User.objects.create_user(username='rider2', email='registered@example.com', password='password123')
        res = self.client.post(reverse('accounts:password_reset'), {'email': 'registered@example.com'})
        self.assertEqual(res.status_code, 302)
        self.assertIn('/account/password-reset/done/', res.url)
