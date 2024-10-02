from django.contrib import admin
from .models import User, SecretKeyUser, SMSComfirmCode , UserAdmin


class SecretKeyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'key')
    search_fields = ('user__name', 'user__email')


class SMSComfirmCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'generated_at', 'user')
    search_fields = ('code', 'user__name')
    list_filter = ('generated_at', 'user')


class UserAdmins(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_date', 'is_deleted')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('is_deleted', 'created_date')
    readonly_fields = ('created_date',)  # Make created_date read-only


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    search_fields = ['name', 'email']


admin.site.register(UserAdmin, CustomUserAdmin)
admin.site.register(User, UserAdmins)
admin.site.register(SecretKeyUser, SecretKeyUserAdmin)
admin.site.register(SMSComfirmCode, SMSComfirmCodeAdmin)
