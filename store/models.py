from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome or Lucide icon class e.g. fa-bicycle")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'category_slug': self.slug})


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Subcategories'
        unique_together = ('category', 'slug')
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('ebike', 'Electric Bike'),
        ('spare_part', 'Spare Part'),
        ('accessory', 'Accessory'),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    SKU = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_products', help_text="Primary category")
    categories = models.ManyToManyField(Category, related_name='products', blank=True, help_text="All categories this product belongs to")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='ebike')
    description = models.TextField()
    short_description = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    
    # Specs & Features
    brand = models.CharField(max_length=100, default='VoltRide')
    model = models.CharField(max_length=100, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    warranty = models.CharField(max_length=100, default='2 Years Limited Warranty')
    
    # E-Bike specific specs
    battery_capacity = models.CharField(max_length=100, blank=True)
    motor_power = models.CharField(max_length=100, blank=True)
    maximum_speed = models.CharField(max_length=50, blank=True)
    range = models.CharField(max_length=100, blank=True)
    charging_time = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    compatibility = models.TextField(blank=True, help_text="Compatibility details for spare parts & components")
    
    # Flags & Timestamps
    featured = models.BooleanField(default=False)
    bestseller = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        if self.category_id and not self.categories.filter(pk=self.category_id).exists():
            self.categories.add(self.category_id)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def is_on_sale(self):
        return bool(self.sale_price and self.sale_price < self.price)

    @property
    def discount_percent(self):
        if self.is_on_sale and self.price > 0:
            diff = self.price - self.sale_price
            return int((diff / self.price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return 'Out of Stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            return f'Low Stock ({self.stock_quantity} left)'
        return 'In Stock'

    @property
    def average_rating(self):
        approved_reviews = self.reviews.filter(approved=True)
        if approved_reviews.exists():
            total = sum(r.rating for r in approved_reviews)
            return round(total / approved_reviews.count(), 1)
        return 5.0

    @property
    def review_count(self):
        return self.reviews.filter(approved=True).count()

    @property
    def reviews_count(self):
        return self.review_count

    @property
    def star_range(self):
        return range(int(self.average_rating))

    @property
    def empty_star_range(self):
        return range(5 - int(self.average_rating))

    def get_primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.product.name} ({'Primary' if self.is_primary else 'Gallery'})"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
