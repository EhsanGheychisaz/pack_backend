from django.contrib import admin
from .models import Shop

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'x_gis', 'y_gis')  # Displayed columns in the list view
    list_filter = ('status',)  # Filters to easily view active/inactive shops
    search_fields = ('name', 'email', 'phone')  # Fields that can be searched
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'password', 'status', 'logo', 'x_gis', 'y_gis')
        }),
    )

# Register the Shop model to appear in the admin
admin.site.register(Shop, ShopAdmin)
