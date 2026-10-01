from django.test import TestCase, Client
from django.urls import reverse
from pages.models import ContactMessage, NewsletterSubscriber


class PagesTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_static_pages_render(self):
        urls = [
            'pages:home',
            'pages:about',
            'pages:services',
            'pages:contact',
            'pages:faq',
            'pages:shipping_policy',
            'pages:returns_policy',
            'pages:privacy_policy',
            'pages:terms_conditions',
            'pages:robots_txt',
        ]
        for url_name in urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, f"Failed on {url_name}")

    def test_contact_form_submission(self):
        payload = {
            'name': 'Sarah Connor',
            'email': 'sarah@example.com',
            'phone': '+1 555-0199',
            'subject': 'Mountain X Question',
            'message': 'What is the torque rating on the mid-drive motor?'
        }
        response = self.client.post(reverse('pages:contact'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(email='sarah@example.com').exists())

    def test_newsletter_subscription(self):
        res = self.client.post(
            reverse('pages:newsletter_subscribe'),
            {'email': 'testsub@example.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'success')
        self.assertTrue(NewsletterSubscriber.objects.filter(email='testsub@example.com').exists())
