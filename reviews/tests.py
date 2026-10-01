from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product
from reviews.models import ProductReview


class ReviewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='reviewer', password='password123')
        self.category = Category.objects.create(name="Batteries", slug="batteries")
        self.product = Product.objects.create(
            name="48V Battery",
            slug="48v-battery",
            SKU="BAT-48",
            category=self.category,
            product_type="spare_part",
            price=Decimal("499.00"),
            stock_quantity=5
        )

    def test_review_submission_and_duplicate_prevention(self):
        self.client.login(username='reviewer', password='password123')
        add_url = reverse('reviews:add_review', kwargs={'product_id': self.product.id})
        
        # Submit first review
        res = self.client.post(add_url, {
            'rating': 5,
            'title': 'Best battery on the market',
            'comment': 'Provides tremendous mileage and steady voltage under high load.'
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(ProductReview.objects.filter(product=self.product).count(), 1)

        # Try duplicate review
        res_dup = self.client.post(add_url, {
            'rating': 4,
            'title': 'Another review',
            'comment': 'Duplicate comment attempt.'
        })
        self.assertEqual(res_dup.status_code, 302)
        self.assertEqual(ProductReview.objects.filter(product=self.product).count(), 1)

    def test_reviews_list_view(self):
        # Create a sample review
        ProductReview.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            title='Outstanding Quality',
            comment='Super reliable power output.',
            approved=True
        )
        url = reverse('reviews:review_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Outstanding Quality')
        self.assertContains(res, 'Verified Reviews')

