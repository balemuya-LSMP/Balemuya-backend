from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    list_per_page = 10

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
    )

admin.site.register(Category, CategoryAdmin)
