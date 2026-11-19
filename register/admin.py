from django.contrib import admin
from .models import Campus, UserProfile


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'created_at')
    search_fields = ('name', 'code', 'location')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'campus', 'department', 'batch_year', 'role', 'roll_number')
    list_filter = ('campus', 'department', 'role', 'batch_year')
    search_fields = ('user__username', 'roll_number')

