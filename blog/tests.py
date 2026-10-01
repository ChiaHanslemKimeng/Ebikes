from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import BlogCategory, BlogPost


class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username='writer', password='password123')
        self.cat = BlogCategory.objects.create(name='Maintenance', slug='maintenance')
        self.post = BlogPost.objects.create(
            title='E-Bike Battery Care',
            slug='e-bike-battery-care',
            category=self.cat,
            author=self.author,
            excerpt='Short summary about lithium battery maintenance.',
            content='Full guide explaining temperature and charging cycles.',
            published=True
        )

    def test_blog_listing(self):
        res = self.client.get(reverse('blog:post_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "E-Bike Battery Care")

    def test_blog_detail_and_view_count(self):
        initial_views = self.post.views
        res = self.client.get(reverse('blog:post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Full guide explaining temperature")
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, initial_views + 1)
