from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Subcategory, Product, ProductImage, Wishlist
from store.cart import Cart


class StoreModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electric Bikes", slug="electric-bikes")
        self.product = Product.objects.create(
            name="VoltRide City Pro",
            slug="voltride-city-pro",
            SKU="VR-TST-001",
            category=self.category,
            product_type="ebike",
            price=Decimal("1500.00"),
            sale_price=Decimal("1200.00"),
            stock_quantity=10,
            low_stock_threshold=3,
            brand="VoltRide",
            motor_power="500W"
        )

    def test_product_pricing_and_sale(self):
        self.assertEqual(self.product.current_price, Decimal("1200.00"))
        self.assertTrue(self.product.is_on_sale)
        self.assertEqual(self.product.discount_percent, 20)

    def test_stock_status(self):
        self.assertTrue(self.product.is_in_stock)
        self.assertEqual(self.product.stock_status, "In Stock")
        self.product.stock_quantity = 2
        self.assertEqual(self.product.stock_status, "Low Stock (2 left)")
        self.product.stock_quantity = 0
        self.assertEqual(self.product.stock_status, "Out of Stock")


class StoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testrider", password="password123")
        self.category = Category.objects.create(name="E-Bikes", slug="e-bikes")
        self.product = Product.objects.create(
            name="VoltRide Fold",
            slug="voltride-fold",
            SKU="VR-FLD-01",
            category=self.category,
            product_type="ebike",
            price=Decimal("1400.00"),
            stock_quantity=5
        )

    def test_shop_listing(self):
        response = self.client.get(reverse('store:shop'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VoltRide Fold")

    def test_shop_category_filter(self):
        response = self.client.get(reverse('store:shop') + f'?category={self.category.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VoltRide Fold")

    def test_product_detail(self):
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VoltRide Fold")
        self.assertContains(response, "VR-FLD-01")

    def test_quick_view_api(self):
        response = self.client.get(reverse('store:product_quick_view', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], "VoltRide Fold")
        self.assertEqual(data['sku'], "VR-FLD-01")

    def test_cart_operations(self):
        # Add to cart
        add_url = reverse('store:cart_add', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url, {'quantity': 2}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['cart_count'], 2)

        # Check cart page
        cart_page = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(cart_page.status_code, 200)
        self.assertContains(cart_page, "VoltRide Fold")

        # Update quantity
        update_url = reverse('store:cart_update', kwargs={'product_id': self.product.id})
        self.client.post(update_url, {'quantity': 3})

        # Remove from cart
        remove_url = reverse('store:cart_remove', kwargs={'product_id': self.product.id})
        self.client.post(remove_url)
        empty_cart = self.client.get(reverse('store:cart_detail'))
        self.assertContains(empty_cart, "Your Shopping Cart is Empty")

    def test_wishlist_toggle(self):
        self.client.login(username="testrider", password="password123")
        toggle_url = reverse('store:wishlist_toggle', kwargs={'product_id': self.product.id})
        
        # Add to wishlist
        res = self.client.post(toggle_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['action'], 'added')
        self.assertTrue(Wishlist.objects.filter(user=self.user, product=self.product).exists())

        # Remove from wishlist
        res2 = self.client.post(toggle_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()['action'], 'removed')
        self.assertFalse(Wishlist.objects.filter(user=self.user, product=self.product).exists())
