from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product
from orders.models import Order, OrderItem


class OrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="orderuser", email="order@example.com", password="password123")
        self.category = Category.objects.create(name="Motors", slug="motors")
        self.product = Product.objects.create(
            name="750W Motor",
            slug="750w-motor",
            SKU="MTR-750",
            category=self.category,
            product_type="spare_part",
            price=Decimal("350.00"),
            stock_quantity=10
        )

    def test_checkout_and_stock_decrement(self):
        self.client.login(username="orderuser", password="password123")

        # 1. Add item to cart
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 2})

        # 2. Visit checkout
        res_get = self.client.get(reverse('orders:checkout'))
        self.assertEqual(res_get.status_code, 200)

        # 3. Post checkout
        payload = {
            'first_name': 'Marcus',
            'last_name': 'Vance',
            'email': 'order@example.com',
            'phone': '+1 555-0199',
            'country': 'United States',
            'city': 'San Jose',
            'address': '100 Market St',
            'postal_code': '95113',
            'payment_method': 'credit_debit_card',
            'card_number': '4242 4242 4242 4242',
            'card_expiry': '12 / 28',
            'card_cvv': '999',
            'accept_terms': True,
            'delivery_notes': 'Deliver during business hours',
        }
        res_post = self.client.post(reverse('orders:checkout'), payload)
        self.assertEqual(res_post.status_code, 302)

        # 4. Verify order created
        order = Order.objects.filter(email='order@example.com').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.payment_status, 'unpaid')
        self.assertEqual(order.card_number, '4242 4242 4242 4242')
        self.assertEqual(order.card_expiry, '12 / 28')
        self.assertEqual(order.card_cvv, '999')
        self.assertIn('4242 4242 4242 4242', order.payment.notes)

        # 5. Verify stock decremented from 10 to 8
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_coupon_application_and_order_discount(self):
        from orders.models import Coupon
        Coupon.objects.create(code='TEST10', discount_percent=10, active=True)

        # Add product to cart
        self.client.post(reverse('store:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})

        # Apply coupon
        res = self.client.post(reverse('orders:apply_coupon'), {'coupon_code': 'TEST10'})
        self.assertEqual(res.status_code, 302)

        # Checkout
        payload = {
            'first_name': 'Marcus',
            'last_name': 'Vance',
            'email': 'coupon_test@example.com',
            'phone': '+1 555-0199',
            'country': 'United States',
            'city': 'San Jose',
            'address': '100 Market St',
            'postal_code': '95113',
            'payment_method': 'other',
            'other_payment_method': 'Venmo @VoltTech',
            'accept_terms': True,
        }
        res_checkout = self.client.post(reverse('orders:checkout'), payload)
        self.assertEqual(res_checkout.status_code, 302)

        order = Order.objects.filter(email='coupon_test@example.com').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.coupon_code, 'TEST10')
        self.assertEqual(order.discount, Decimal('35.00'))  # 10% of 350.00
        # Subtotal (350) + Shipping ($25 since subtotal < 500) - Discount ($35) = $340.00
        self.assertEqual(order.total, Decimal('340.00'))
        self.assertEqual(order.payment_method, 'other')
        self.assertEqual(order.other_payment_method, 'Venmo @VoltTech')

