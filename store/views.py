from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count

from store.models import Product, Category, Subcategory, Wishlist, ProductImage
from store.cart import Cart
from reviews.models import ProductReview


def get_current_wishlist_ids(request):
    """Helper to return set of product IDs in wishlist for both guests and authenticated users."""
    if request.user.is_authenticated:
        # Also merge session wishlist into DB if any exists
        session_wishlist = request.session.get('voltride_wishlist', [])
        if session_wishlist:
            for pid in session_wishlist:
                prod = Product.objects.filter(id=pid, active=True).first()
                if prod:
                    Wishlist.objects.get_or_create(user=request.user, product=prod)
            request.session['voltride_wishlist'] = []
            request.session.modified = True
        return set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        return set(request.session.get('voltride_wishlist', []))


def shop_view(request):
    """
    Shop listing page supporting multi-attribute filtering,
    sorting, search, and pagination.
    """
    products = Product.objects.filter(active=True).select_related('category', 'subcategory').prefetch_related('images', 'reviews')

    # Filter by category slug
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # Filter by subcategory slug
    subcategory_slug = request.GET.get('subcategory')
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)

    # Filter by product type
    product_type = request.GET.get('type')
    if product_type in ['ebike', 'spare_part', 'accessory']:
        if not current_category or products.filter(product_type=product_type).exists():
            products = products.filter(product_type=product_type)
        else:
            product_type = None

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass

    # Filter by availability
    in_stock = request.GET.get('in_stock')
    if in_stock == '1':
        products = products.filter(stock_quantity__gt=0)

    # Filter by search keyword
    q = request.GET.get('q')
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(short_description__icontains=q) |
            Q(SKU__icontains=q) |
            Q(brand__icontains=q) |
            Q(compatibility__icontains=q)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-bestseller', '-created_at')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', '-created_at')
    else:  # newest
        products = products.order_by('-created_at')

    # Available filter metadata for sidebar
    categories = Category.objects.all().prefetch_related('subcategories')

    # Pagination (9 per page)
    paginator = Paginator(products, 9)
    page = request.GET.get('page', 1)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    user_wishlist_ids = get_current_wishlist_ids(request)

    context = {
        'products': products_page,
        'total_count': products.count(),
        'categories': categories,
        'current_category': current_category,
        'current_sort': sort_by,
        'current_type': product_type,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'q': q,
        'user_wishlist_ids': user_wishlist_ids,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('format') == 'partial':
        return render(request, 'shop/partials/product_grid.html', context)

    return render(request, 'shop/shop.html', context)


def category_detail_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    return redirect(f"/shop/?category={category.slug}")


def product_detail_view(request, slug):
    """
    Detailed product showcase with gallery, tech specs,
    compatibility data, reviews, and related products in swiper.
    """
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory').prefetch_related('images', 'reviews__user'),
        slug=slug,
        active=True
    )

    approved_reviews = product.reviews.filter(approved=True).select_related('user').order_by('-created_at')
    
    # Related products from same category (up to 8 for the swiper)
    related_products = Product.objects.filter(
        category=product.category,
        active=True
    ).exclude(id=product.id)[:8]

    user_has_reviewed = False
    user_wishlist_ids = get_current_wishlist_ids(request)
    is_in_wishlist = product.id in user_wishlist_ids

    if request.user.is_authenticated:
        user_has_reviewed = approved_reviews.filter(user=request.user).exists()

    context = {
        'product': product,
        'reviews': approved_reviews,
        'reviews_count': approved_reviews.count(),
        'related_products': related_products,
        'user_has_reviewed': user_has_reviewed,
        'is_in_wishlist': is_in_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'products/product_detail.html', context)


def product_quick_view(request, slug):
    """
    AJAX endpoint returning product details JSON for quick view modal.
    """
    product = get_object_or_404(Product, slug=slug, active=True)
    primary_img = product.get_primary_image()
    image_url = primary_img.image.url if primary_img and primary_img.image else '/static/images/placeholder-bike.svg'

    data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'url': product.get_absolute_url(),
        'sku': product.SKU,
        'price': str(product.price),
        'sale_price': str(product.sale_price) if product.sale_price else None,
        'current_price': str(product.current_price),
        'is_on_sale': product.is_on_sale,
        'discount_percent': product.discount_percent,
        'stock_status': product.stock_status,
        'is_in_stock': product.is_in_stock,
        'stock_quantity': product.stock_quantity,
        'short_description': product.short_description or product.description[:180] + '...',
        'image_url': image_url,
        'category': product.category.name,
        'average_rating': product.average_rating,
        'review_count': product.review_count,
        'battery_capacity': product.battery_capacity,
        'motor_power': product.motor_power,
        'range': product.range,
        'maximum_speed': product.maximum_speed,
        'warranty': product.warranty,
    }
    return JsonResponse(data)


# ------------------ CART VIEWS ------------------

def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


@require_POST
def cart_add_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, active=True)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        quantity = 1

    if not product.is_in_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': f'"{product.name}" is currently out of stock.'}, status=400)
        messages.error(request, f'"{product.name}" is currently out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'store:shop'))

    added_qty = cart.add(product=product, quantity=quantity)

    success_msg = f'Added {quantity}x "{product.name}" to your cart.'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': success_msg,
            'cart_count': len(cart),
            'cart_subtotal': str(cart.get_subtotal()),
            'cart_shipping': str(cart.get_shipping_cost()),
            'cart_total': str(cart.get_total_price()),
        })

    messages.success(request, success_msg)
    if request.POST.get('buy_now') == '1':
        return redirect('orders:checkout')
    return redirect(request.META.get('HTTP_REFERER', 'store:cart_detail'))


@require_POST
def cart_update_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    new_qty = cart.update_quantity(product=product, quantity=quantity)
    item_total = str(product.current_price * new_qty) if new_qty > 0 else '0.00'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'quantity': new_qty,
            'item_total': item_total,
            'cart_count': len(cart),
            'cart_subtotal': str(cart.get_subtotal()),
            'cart_shipping': str(cart.get_shipping_cost()),
            'cart_total': str(cart.get_total_price()),
        })

    messages.info(request, f'Cart updated for "{product.name}".')
    return redirect('store:cart_detail')


@require_POST
def cart_remove_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Removed "{product.name}" from your cart.',
            'cart_count': len(cart),
            'cart_subtotal': str(cart.get_subtotal()),
            'cart_shipping': str(cart.get_shipping_cost()),
            'cart_total': str(cart.get_total_price()),
        })

    messages.info(request, f'Removed "{product.name}" from your cart.')
    return redirect('store:cart_detail')


def cart_clear_view(request):
    cart = Cart(request)
    cart.clear()
    messages.info(request, 'Your cart has been cleared.')
    return redirect('store:cart_detail')


# ------------------ WISHLIST VIEWS (Supports GUESTS & AUTHENTICATED) ------------------

def wishlist_view(request):
    """
    Display wishlist for both authenticated users and guests.
    """
    if request.user.is_authenticated:
        wishlist_ids = get_current_wishlist_ids(request)
        products = Product.objects.filter(id__in=wishlist_ids, active=True).select_related('category').prefetch_related('images')
    else:
        guest_ids = request.session.get('voltride_wishlist', [])
        products = Product.objects.filter(id__in=guest_ids, active=True).select_related('category').prefetch_related('images')

    return render(request, 'accounts/wishlist.html', {'wishlist_products': products})


@require_POST
def wishlist_toggle_view(request, product_id):
    """
    Toggle product in wishlist for both guests and authenticated users.
    No login required!
    """
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            action = 'added'
            message = f'Added "{product.name}" to your wishlist.'
        else:
            item.delete()
            action = 'removed'
            message = f'Removed "{product.name}" from your wishlist.'
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        # Session-based guest wishlist
        guest_wishlist = request.session.get('voltride_wishlist', [])
        if product.id in guest_wishlist:
            guest_wishlist.remove(product.id)
            action = 'removed'
            message = f'Removed "{product.name}" from your wishlist.'
        else:
            guest_wishlist.append(product.id)
            action = 'added'
            message = f'Added "{product.name}" to your wishlist.'
        request.session['voltride_wishlist'] = guest_wishlist
        request.session.modified = True
        wishlist_count = len(guest_wishlist)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'message': message,
            'wishlist_count': wishlist_count,
        })

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'store:shop'))
