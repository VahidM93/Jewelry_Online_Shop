from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import Account, OtpCode
from django.contrib.auth.models import Group


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created')
    list_per_page = 10


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    readonly_fields = ('last_login',)
    list_display = ('email', 'phone_number', 'is_admin', 'is_superuser')
    list_filter = ('is_admin', 'phone_number')

    fieldsets = (
        ('Main', {'fields': ('email', 'phone_number', 'full_name', 'password', 'last_login')}),
        ('Permissions',
         {'classes': ('collapse',),
          'fields': (('is_active', 'is_admin', 'is_superuser'), 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'full_name', 'password1', 'password2')}),
    )

    search_fields = ('email', 'full_name')
    ordering = ('full_name',)
    filter_horizontal = ('groups', 'user_permissions')
    list_per_page = 10

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form

# Now register the new UserAdmin...
admin.site.register(Account, UserAdmin)

