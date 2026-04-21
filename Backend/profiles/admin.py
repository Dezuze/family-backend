
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Gallery, CommunityRole
from image_cropping import ImageCroppingMixin

@admin.register(Gallery)
class GalleryAdmin(ModelAdmin):
    list_display = ('id', 'date', 'description', 'image', 'created_at')
    list_filter = ('date',)
    search_fields = ('description',)



@admin.register(CommunityRole)
class CommunityRoleAdmin(ModelAdmin):
    list_display = ('name', 'priority', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
