from decimal import Decimal
from django.conf import settings
from store.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        current_stock = product.stock_quantity

        if product_id not in self.cart:
            qty_to_add = min(quantity, current_stock)
            if qty_to_add > 0:
                self.cart[product_id] = {
                    'quantity': qty_to_add,
                    'price': str(product.current_price)
                }
        else:
            if override_quantity:
                new_qty = min(quantity, current_stock)
            else:
                new_qty = min(self.cart[product_id]['quantity'] + quantity, current_stock)
            
            if new_qty > 0:
                self.cart[product_id]['quantity'] = new_qty
                self.cart[product_id]['price'] = str(product.current_price)
            else:
                self.remove(product)
                return 0
        
        self.save()
        return self.cart.get(product_id, {}).get('quantity', 0)

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update_quantity(self, product, quantity):
        return self.add(product, quantity=quantity, override_quantity=True)

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).select_related('category')
        product_map = {str(p.id): p for p in products}

        cart_copy = self.cart.copy()
        for product_id, item_data in cart_copy.items():
            product = product_map.get(product_id)
            if not product or not product.active or product.stock_quantity == 0:
                # Remove stale or out-of-stock item
                self.remove_by_id(product_id)
                continue
            
            # Ensure quantity doesn't exceed current stock
            if item_data['quantity'] > product.stock_quantity:
                item_data['quantity'] = product.stock_quantity
                self.cart[product_id]['quantity'] = product.stock_quantity
                self.save()

            item = item_data.copy()
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def remove_by_id(self, product_id):
        if str(product_id) in self.cart:
            del self.cart[str(product_id)]
            self.save()

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        subtotal = Decimal('0.00')
        for item in self:
            subtotal += item['total_price']
        return subtotal

    def get_shipping_cost(self):
        subtotal = self.get_subtotal()
        if subtotal == 0:
            return Decimal('0.00')
        # Free shipping on orders over $500 or selected criteria
        if subtotal >= Decimal('500.00'):
            return Decimal('0.00')
        return Decimal('25.00')

    def get_amount_to_free_shipping(self):
        subtotal = self.get_subtotal()
        threshold = Decimal('500.00')
        if subtotal >= threshold:
            return Decimal('0.00')
        return threshold - subtotal

    def get_free_shipping_progress(self):
        subtotal = self.get_subtotal()
        if subtotal >= Decimal('500.00'):
            return 100
        return min(100, int((subtotal / Decimal('500.00')) * 100))

    def get_coupon(self):
        code = self.session.get('coupon_code')
        if code:
            try:
                from orders.models import Coupon
                return Coupon.objects.get(code__iexact=code, active=True)
            except Exception:
                return None
        return None

    def get_discount(self):
        coupon = self.get_coupon()
        if coupon:
            return coupon.calculate_discount(self.get_subtotal())
        return Decimal('0.00')

    def get_total_price(self):
        subtotal = self.get_subtotal()
        shipping = self.get_shipping_cost()
        discount = self.get_discount()
        total = subtotal + shipping - discount
        return max(Decimal('0.00'), total)

    MIN_ORDER_AMOUNT = Decimal('200.00')

    def meets_min_order(self):
        return self.get_subtotal() >= self.MIN_ORDER_AMOUNT

    def get_remaining_for_min_order(self):
        subtotal = self.get_subtotal()
        if subtotal >= self.MIN_ORDER_AMOUNT:
            return Decimal('0.00')
        return self.MIN_ORDER_AMOUNT - subtotal

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        if 'coupon_code' in self.session:
            del self.session['coupon_code']
        self.save()
