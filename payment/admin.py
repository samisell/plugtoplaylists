from django.contrib import admin
from .models import Package

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_editable = ('price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')