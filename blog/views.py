from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from blog.models import BlogPost, BlogCategory


def post_list_view(request):
    """
    Blog index listing with category filtering, search, and pagination.
    """
    posts = BlogPost.objects.filter(published=True).select_related('category', 'author')

    # Category filter
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=current_category)

    # Tag filter
    tag = request.GET.get('tag')
    if tag:
        posts = posts.filter(tags__icontains=tag)

    # Search filter
    q = request.GET.get('q')
    if q:
        posts = posts.filter(
            Q(title__icontains=q) |
            Q(excerpt__icontains=q) |
            Q(content__icontains=q) |
            Q(tags__icontains=q)
        )

    categories = BlogCategory.objects.all()
    recent_posts = BlogPost.objects.filter(published=True).order_by('-published_at')[:5]

    paginator = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    context = {
        'posts': posts_page,
        'categories': categories,
        'current_category': current_category,
        'recent_posts': recent_posts,
        'q': q,
        'tag': tag,
    }
    return render(request, 'blog/blog_list.html', context)


def post_detail_view(request, slug):
    """
    Individual blog post with related articles and views increment.
    """
    post = get_object_or_404(BlogPost.objects.select_related('category', 'author'), slug=slug, published=True)
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])

    # Related posts in same category
    related_posts = BlogPost.objects.filter(
        category=post.category,
        published=True
    ).exclude(id=post.id)[:3]

    recent_posts = BlogPost.objects.filter(published=True).exclude(id=post.id).order_by('-published_at')[:4]
    categories = BlogCategory.objects.all()

    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    return render(request, 'blog/blog_detail.html', context)
