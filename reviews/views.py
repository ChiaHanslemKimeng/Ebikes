from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Avg

from store.models import Product
from reviews.models import ProductReview
from reviews.forms import ProductReviewForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from orders.models import OrderItem


def review_list_view(request):
    """
    Public reviews page showcasing customer feedback and verified ratings with pagination.
    """
    reviews_qs = ProductReview.objects.filter(approved=True).select_related('product', 'user').order_by('-created_at')

    # Optional filter by rating
    rating_param = request.GET.get('rating')
    if rating_param and rating_param.isdigit():
        reviews_qs = reviews_qs.filter(rating=int(rating_param))

    total_reviews = ProductReview.objects.filter(approved=True).count()
    filtered_reviews_count = reviews_qs.count()
    avg_rating_val = ProductReview.objects.filter(approved=True).aggregate(avg=Avg('rating'))['avg'] or 4.9

    star_counts = {
        5: ProductReview.objects.filter(approved=True, rating=5).count(),
        4: ProductReview.objects.filter(approved=True, rating=4).count(),
        3: ProductReview.objects.filter(approved=True, rating=3).count(),
        2: ProductReview.objects.filter(approved=True, rating=2).count(),
        1: ProductReview.objects.filter(approved=True, rating=1).count(),
    }

    paginator = Paginator(reviews_qs, 9)  # 9 reviews per page (3x3 grid)
    page = request.GET.get('page')
    try:
        reviews_page = paginator.page(page)
    except PageNotAnInteger:
        reviews_page = paginator.page(1)
    except EmptyPage:
        reviews_page = paginator.page(paginator.num_pages)

    context = {
        'reviews': reviews_page,
        'page_obj': reviews_page,
        'total_reviews': total_reviews,
        'filtered_reviews_count': filtered_reviews_count,
        'avg_rating': round(avg_rating_val, 1),
        'star_counts': star_counts,
        'current_rating': rating_param,
    }
    return render(request, 'reviews/review_list.html', context)



@login_required
@require_POST
def add_review_view(request, product_id):
    """
    Handle product review submission with verified purchase detection.
    """
    product = get_object_or_404(Product, id=product_id, active=True)
    
    # Check for existing review by this user
    if ProductReview.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, f'You have already submitted a review for "{product.name}".')
        return redirect(product.get_absolute_url())

    form = ProductReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        
        # Check if user actually bought this product
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()
        review.verified_purchase = has_purchased
        review.approved = True  # Auto-approve for seamless user experience
        review.save()

        messages.success(request, f'Thank you! Your {review.rating}★ review for "{product.name}" has been published.')
    else:
        messages.error(request, 'Unable to submit review. Please check all fields.')

    return redirect(product.get_absolute_url())
