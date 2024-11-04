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


from .models import Container


class ContainerAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'guarantee_amount', 'country', 'date', 'shop')
    search_fields = ('code', 'shop__name')  # Adjust as necessary to match your fields
    list_filter = ('type', 'country', 'shop')

    def save_model(self, request, obj, form, change):
        # Automatically generate code if it's not set
        if not obj.code:
            obj.code = obj.generate_code()
        super().save_model(request, obj, form, change)


admin.site.register(Container, ContainerAdmin)
admin.site.register(UserPackInfo, UserPackInfoAdmin)
admin.site.register(UserPacks, UserPacksAdmin)

from django.contrib import admin
from .models import ContainerRequest

class ContainerRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'requested_by', 'request_date', 'status']
    list_filter = ['status', 'shop']

admin.site.register(ContainerRequest, ContainerRequestAdmin)
