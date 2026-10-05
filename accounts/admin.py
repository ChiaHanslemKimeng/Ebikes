from django.contrib import admin
from accounts.models import UserProfile, PushSubscription


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    list_filter = ('country', 'created_at')


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint_truncated', 'created_at', 'updated_at')
    search_fields = ('user__username', 'endpoint')
    list_filter = ('created_at',)

    def endpoint_truncated(self, obj):
        return obj.endpoint[:60] + "..." if len(obj.endpoint) > 60 else obj.endpoint
    endpoint_truncated.short_description = "Push Endpoint"
