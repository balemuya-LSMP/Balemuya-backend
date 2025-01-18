from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'id')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ('name',)
    list_per_page = 10

    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
    )

admin.site.register(Category, CategoryAdmin)
