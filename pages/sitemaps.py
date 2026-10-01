from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from store.models import Product, Category
from blog.models import BlogPost


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'pages:home',
            'store:shop',
            'pages:about',
            'pages:services',
            'reviews:review_list',
            'pages:contact',
            'pages:faq',
            'blog:post_list',
            'pages:shipping_policy',
            'pages:returns_policy',
            'pages:privacy_policy',
            'pages:terms_conditions',
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Product.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()


class BlogSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at
