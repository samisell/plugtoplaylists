from django.contrib import admin
from .models import SupportRequest

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message', 'user__username')
    list_editable = ('status',)