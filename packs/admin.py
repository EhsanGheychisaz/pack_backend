from django.contrib import admin
from .models import UserPackInfo, UserPacks

class UserPacksInline(admin.TabularInline):
    model = UserPacks
    extra = 1  # Number of empty forms to display

class UserPackInfoAdmin(admin.ModelAdmin):
    inlines = [UserPacksInline]
    list_display = ('user', 'count')
    search_fields = ('user__name', 'user__email')

class UserPacksAdmin(admin.ModelAdmin):
    list_display = ('user_pack_id', 'given_date', 'due_date')
    list_filter = ('given_date', 'due_date')
    search_fields = ('pack_title', 'pack_description')

admin.site.register(UserPackInfo, UserPackInfoAdmin)
admin.site.register(UserPacks, UserPacksAdmin)
