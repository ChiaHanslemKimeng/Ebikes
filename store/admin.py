from django.contrib import admin
from django.utils.html import format_html
from store.models import Category, Subcategory, Product, ProductImage, Wishlist


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'is_featured', 'order', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'order')
    search_fields = ('name', 'description')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'SKU',
        'category',
        'price_display',
        'stock_badge',
        'product_type',
        'active',
        'featured',
        'bestseller',
        'new_arrival'
    )
    list_filter = ('active', 'featured', 'bestseller', 'product_type', 'category', 'brand')
    search_fields = ('name', 'SKU', 'description', 'brand', 'model')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('active', 'featured', 'bestseller')
    inlines = [ProductImageInline]
    actions = ['make_active', 'make_inactive', 'mark_featured', 'mark_bestseller']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'SKU', 'category', 'subcategory', 'product_type', 'brand', 'model')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'sale_price', 'cost_price', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Technical Specifications (E-Bikes & Power)', {
            'classes': ('collapse',),
            'fields': (
                'motor_power', 'battery_capacity', 'maximum_speed', 'range',
                'charging_time', 'weight', 'dimensions', 'color', 'material',
                'warranty', 'compatibility'
            )
        }),
        ('Descriptions & Marketing', {
            'fields': ('short_description', 'description')
        }),
        ('Visibility & Badges', {
            'fields': ('active', 'featured', 'bestseller', 'new_arrival')
        }),
    )

    def price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="color:#10b981; font-weight:bold;">${}</span> <del style="color:#94a3b8; font-size:11px;">${}</del>',
                obj.sale_price, obj.price
            )
        return f"${obj.price}"
    price_display.short_description = "Price"

    def stock_badge(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color:#ef4444; font-weight:bold;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color:#f59e0b; font-weight:bold;">Low ({} left)</span>', obj.stock_quantity)
        return format_html('<span style="color:#10b981;">{} in stock</span>', obj.stock_quantity)
    stock_badge.short_description = "Inventory"

    @admin.action(description="Mark selected products as Active")
    def make_active(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Mark selected products as Inactive")
    def make_inactive(self, request, queryset):
        queryset.update(active=False)

    @admin.action(description="Mark selected products as Featured")
    def mark_featured(self, request, queryset):
        queryset.update(featured=True)

    @admin.action(description="Mark selected products as Bestseller")
    def mark_bestseller(self, request, queryset):
        queryset.update(bestseller=True)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
