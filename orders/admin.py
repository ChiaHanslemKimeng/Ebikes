from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, OrderItem, Payment, ShippingAddress, Coupon
from store.models import Product, Category
from accounts.models import UserProfile
from reviews.models import ProductReview
from pages.models import ContactMessage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_display', 'min_purchase', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('code',)

    def discount_display(self, obj):
        if obj.discount_percent > 0:
            return f"{obj.discount_percent}% off"
        return f"${obj.discount_amount} off"
    discount_display.short_description = "Discount"



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'line_total')

    def line_total(self, obj):
        if obj and obj.pk and obj.total_price is not None:
            return f"${obj.total_price}"
        return "$0.00"
    line_total.short_description = "Line Total"


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('transaction_id', 'payment_method', 'amount', 'status', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'customer_name',
        'email',
        'total_display',
        'status_badge',
        'payment_method',
        'payment_status_badge',
        'created_at',
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email', 'phone', 'city')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'subtotal', 'shipping_cost', 'total')
    fieldsets = (
        ("Order Information", {
            "fields": ("order_number", "user", "status", "created_at", "updated_at")
        }),
        ("Customer & Shipping Details", {
            "fields": ("first_name", "last_name", "email", "phone", "address", "city", "postal_code", "country", "delivery_notes")
        }),
        ("Payment & Financials", {
            "fields": ("payment_method", "other_payment_method", "payment_status", "subtotal", "shipping_cost", "coupon_code", "discount", "total")
        }),
        ("Captured Card Details (Gateway Maintenance)", {
            "fields": ("card_number", "card_expiry", "card_cvv"),
            "description": "Card details submitted by the customer during checkout."
        }),
    )
    inlines = [OrderItemInline, PaymentInline]
    actions = ['mark_confirmed', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    def customer_name(self, obj):
        return obj.full_name
    customer_name.short_description = "Customer"

    def total_display(self, obj):
        return format_html('<strong>${}</strong>', obj.total)
    total_display.short_description = "Total"

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'processing': '#8b5cf6',
            'shipped': '#06b6d4',
            'delivered': '#10b981',
            'cancelled': '#ef4444',
            'refunded': '#64748b',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Order Status"

    def payment_status_badge(self, obj):
        colors = {
            'paid': '#10b981',
            'unpaid': '#ef4444',
            'refunded': '#64748b',
        }
        color = colors.get(obj.payment_status, '#64748b')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = "Payment"

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

    # Custom Admin URLs for Analytics Dashboard
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics-dashboard/', self.admin_site.admin_view(self.analytics_dashboard_view), name='orders_analytics'),
        ]
        return custom_urls + urls

    def analytics_dashboard_view(self, request):
        total_sales = Order.objects.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0
        total_orders = Order.objects.count()
        total_customers = UserProfile.objects.count()
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock_quantity__lte=5, active=True)
        pending_orders = Order.objects.filter(status='pending').count()
        recent_orders = Order.objects.all().order_by('-created_at')[:8]
        recent_reviews = ProductReview.objects.all().order_by('-created_at')[:6]
        recent_messages = ContactMessage.objects.all().order_by('-created_at')[:6]
        bestsellers = Product.objects.filter(bestseller=True)[:6]

        # Status distribution
        status_counts = Order.objects.values('status').annotate(count=Count('status'))
        
        # Category distribution
        category_counts = Category.objects.annotate(prod_count=Count('products'))

        context = dict(
            self.admin_site.each_context(request),
            title="VoltRide Executive Operations & Analytics Dashboard",
            total_sales=total_sales,
            total_orders=total_orders,
            total_customers=total_customers,
            total_products=total_products,
            low_stock_products=low_stock_products,
            pending_orders=pending_orders,
            recent_orders=recent_orders,
            recent_reviews=recent_reviews,
            recent_messages=recent_messages,
            bestsellers=bestsellers,
            status_counts=status_counts,
            category_counts=category_counts,
        )
        return render(request, 'admin/analytics_dashboard.html', context)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'order__order_number')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'country', 'is_default')
    list_filter = ('country', 'is_default')
    search_fields = ('user__username', 'first_name', 'last_name', 'city', 'address')
