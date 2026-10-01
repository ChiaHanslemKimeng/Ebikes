from django.contrib import admin
from blog.models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = "Articles"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'published', 'views', 'published_at')
    list_filter = ('published', 'category', 'published_at')
    search_fields = ('title', 'excerpt', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('published',)
    actions = ['publish_posts', 'unpublish_posts']

    @admin.action(description="Publish selected articles")
    def publish_posts(self, request, queryset):
        queryset.update(published=True)

    @admin.action(description="Unpublish selected articles")
    def unpublish_posts(self, request, queryset):
        queryset.update(published=False)
