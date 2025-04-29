from django.contrib import admin
from .models import BlogPost, Media, Comment, Like


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    readonly_fields = ('user', 'created_at')
    can_delete = False


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'updated_at')
    inlines = [MediaInline, CommentInline, LikeInline]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'post', 'created_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('post__title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title', 'content')
    list_filter = ('created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')
    list_filter = ('created_at',)
