from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Media

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'post_type', 'visibility', 'is_auto_generated', 'location', 'created_at')
    list_filter = ('post_type', 'visibility', 'is_auto_generated', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Article Content', {
            'fields': ('creator', 'title', 'description', 'post_type', 'visibility')
        }),
        ('Metadata', {
            'fields': (('location', 'event_date'), 'is_kudumbayogam', 'is_auto_generated', 'generated_kind', 'generated_for_member', 'generated_key')
        }),
    )

@admin.register(Media)
class MediaAdmin(ModelAdmin):
    list_display = ('id', 'uploader', 'post', 'media_type', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at', 'post')
    search_fields = ('media_type', 'caption')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        (None, {
            'fields': (('uploader', 'post'), ('media_type', 'media_url'), 'caption', 'is_personal_gallery')
        }),
    )
