from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from orders.models import Order
from orders.emails import send_user_welcome_email
from store.models import Wishlist
from reviews.models import ProductReview


def register_view(request):
    """
    User registration with auto-login on success.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            phone = form.cleaned_data.get('phone')
            if phone and hasattr(user, 'profile'):
                user.profile.phone = phone
                user.profile.save()
            send_user_welcome_email(user, request)
            messages.success(request, f"Welcome to Surron Bikes & Parts, {user.first_name or user.username}! Your account is created.")
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    User login supporting username or email.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out successfully.")
    return redirect('pages:home')


@login_required
def dashboard_view(request):
    """
    Main user account dashboard showing orders, wishlist, reviews, and profile overview.
    """
    user = request.user
    recent_orders = Order.objects.filter(user=user).prefetch_related('items')[:5]
    total_orders_count = Order.objects.filter(user=user).count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    reviews_count = ProductReview.objects.filter(user=user).count()

    context = {
        'recent_orders': recent_orders,
        'total_orders_count': total_orders_count,
        'wishlist_count': wishlist_count,
        'reviews_count': reviews_count,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_edit_view(request):
    """
    Edit user profile and shipping address preferences.
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile information has been successfully updated.")
            return redirect('accounts:dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile_edit.html', {'u_form': u_form, 'p_form': p_form})


@login_required
def password_change_view(request):
    """
    Change user password with session persistence.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('accounts:dashboard')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})
