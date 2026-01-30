from django.contrib import admin
from .models import News, UserProfile

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'view_counter', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'body')
    ordering = ('-view_counter',)
    list_per_page = 20

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_categories_display')
    search_fields = ('user__username',)
    
    def get_favorite_categories_display(self, obj):
        return ', '.join(obj.favorite_categories) if obj.favorite_categories else 'هیچ'
    get_favorite_categories_display.short_description = 'دسته‌های مورد علاقه'