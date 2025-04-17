from django.contrib import admin
from .models import CustomUser


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')


admin.site.register(CustomUser, UserAdmin)
