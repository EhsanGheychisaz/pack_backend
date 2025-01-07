
from django.contrib import admin
from .models import Shop

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'created_date')  # Columns in the list view
    list_filter = ('status', 'created_date')  # Filters in the list view
    search_fields = ('name', 'email', 'phone')  # Searchable fields
    readonly_fields = ('created_date',)  # Fields that cannot be edited
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'password', 'status', 'logo', 'x_gis', 'y_gis', 'reset_code', 'created_date')
        }),
    )

admin.site.register(Shop, ShopAdmin)
