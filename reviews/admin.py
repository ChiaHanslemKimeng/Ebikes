from django.contrib import admin
from reviews.models import ProductReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'verified_purchase', 'approved', 'created_at')
    list_filter = ('rating', 'approved', 'verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    list_editable = ('approved',)
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.update(approved=False)
