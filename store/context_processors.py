from store.cart import Cart
from store.models import Category, Wishlist


def store_context(request):
    cart = Cart(request)
    
    # Support wishlist count for both guests and authenticated users
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist_count = len(request.session.get('voltride_wishlist', []))
    
    categories = Category.objects.all().prefetch_related('subcategories')
    
    return {
        'cart': cart,
        'cart_count': len(cart),
        'wishlist_count': wishlist_count,
        'all_categories': categories,
    }
