from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from store.models import Product, Category, Wishlist
from store.views import get_current_wishlist_ids
from blog.models import BlogPost
from reviews.models import ProductReview
from pages.forms import ContactForm, NewsletterForm
from pages.models import NewsletterSubscriber, ContactMessage
from orders.emails import send_contact_form_emails


def home_view(request):
    """
    Homepage showcasing:
    - 3-image Hero Banner carousel
    - Featured Categories
    - 10 lastly added products in Swiper
    - Why Choose Us
    - Promotional Banner ("Upgrade Your Ride")
    - What Our Customers Say (9 reviews in Swiper)
    - From the Tech Blog (9 blog posts in Swiper)
    - Newsletter
    """
    featured_categories = Category.objects.filter(is_featured=True).order_by('order')[:8]
    
    # Featured Products in home: Ensure bikes are prominently featured
    featured_bikes = Product.objects.filter(
        active=True,
        product_type='ebike'
    ).select_related('category').prefetch_related('images', 'reviews').order_by('-created_at')[:12]

    # Graceful fallback if no bikes exist
    if not featured_bikes.exists():
        featured_bikes = Product.objects.filter(
            active=True
        ).select_related('category').prefetch_related('images', 'reviews').order_by('-created_at')[:10]
    
    # 9 customer reviews
    customer_reviews_9 = ProductReview.objects.filter(approved=True).select_related('user', 'product').order_by('-created_at')[:9]
    
    # 9 blog posts
    blog_posts_9 = BlogPost.objects.filter(published=True).select_related('category', 'author').order_by('-published_at')[:9]

    user_wishlist_ids = get_current_wishlist_ids(request)

    context = {
        'featured_categories': featured_categories,
        'featured_products': featured_bikes,
        'testimonials': customer_reviews_9,
        'recent_blogs': blog_posts_9,
        'user_wishlist_ids': user_wishlist_ids,
        'newsletter_form': NewsletterForm(),
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def services_view(request):
    return render(request, 'pages/services.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            send_contact_form_emails(contact_msg, request)
            messages.success(request, "Thank you! Your message has been received. Our technical team will get back to you within 24 hours.")
            return redirect('pages:contact')
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})


def faq_view(request):
    return render(request, 'pages/faq.html')


def shipping_policy_view(request):
    return render(request, 'pages/shipping_policy.html')


def returns_policy_view(request):
    return render(request, 'pages/returns_policy.html')


def privacy_policy_view(request):
    return render(request, 'pages/privacy_policy.html')


def terms_conditions_view(request):
    return render(request, 'pages/terms_conditions.html')


def search_view(request):
    """
    Site-wide search returning both matching products and blog articles.
    """
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    posts = BlogPost.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(SKU__icontains=query) |
            Q(brand__icontains=query) |
            Q(compatibility__icontains=query) |
            Q(category__name__icontains=query),
            active=True
        ).distinct().prefetch_related('images', 'reviews')

        posts = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query),
            published=True
        ).distinct()

    user_wishlist_ids = get_current_wishlist_ids(request)

    context = {
        'query': query,
        'products': products,
        'posts': posts,
        'products_count': products.count(),
        'posts_count': posts.count(),
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'pages/search_results.html', context)


def search_autocomplete_view(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(
        Q(name__icontains=query) | Q(category__name__icontains=query),
        active=True
    ).values('id', 'name', 'slug', 'price', 'sale_price', 'category__name')[:5]

    results = []
    for p in products:
        results.append({
            'title': p['name'],
            'url': f"/product/{p['slug']}/",
            'category': p['category__name'],
            'price': str(p['sale_price'] or p['price']),
        })

    return JsonResponse({'results': results})


@require_POST
def newsletter_subscribe_view(request):
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()

    if not email:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Please provide a valid email address.'}, status=400)
        messages.error(request, 'Please provide a valid email address.')
        return redirect(request.META.get('HTTP_REFERER', 'pages:home'))

    sub, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={'name': name, 'is_active': True}
    )

    msg = "Thank you for subscribing to Surron Bikes & Parts updates and exclusive offers!" if created else "You are already subscribed to our newsletter."
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': msg})

    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'pages:home'))


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /account/',
        'Disallow: /cart/',
        'Disallow: /checkout/',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def handler404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def handler403_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def handler500_view(request):
    return render(request, 'errors/500.html', status=500)
