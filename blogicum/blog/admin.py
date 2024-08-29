from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configs"""

    prepopulated_fields = {"slug": ["title"]}
    empty_value_display = '-пусто-'


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin configs"""

    empty_value_display = '-пусто-'
    list_display = ('title', 'category', 'author', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('created_at', 'location', 'author', 'location')
    search_fields = ('title', 'author', 'location')


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    """Location admin configs"""

    empty_value_display = '-пусто-'
