from django.contrib import admin
from .models import *

@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'theme', 'taste_type', 'tea_type', 'no_additives', 'price_range']
    list_filter = ['taste_type', 'tea_type', 'no_additives']

@admin.register(Taste)
class TasteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['id', 'name']

@admin.register(BaseTea)
class BaseTeaAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tea_type', 'price', 'get_tastes', 'making_time', 'temperature']
    list_filter = ['id', 'name', 'tea_type', 'price', 'making_time', 'temperature']
    
    def get_tastes(self, obj):
        return ", ".join([taste.name for taste in obj.tastes.all()[:3]]) + ("..." if obj.tastes.count() > 3 else "")
    get_tastes.short_description = 'Taste'
    
@admin.register(BaseTeaTaste)
class BaseTeaTasteAdmin(admin.ModelAdmin):
    list_display = ['id', 'tea', 'taste']
    list_filter = ['id', 'tea', 'taste']

@admin.register(Additive)
class AdditiveAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['id', 'name']

@admin.register(BaseTaste)
class BaseTasteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['id', 'name']
    
@admin.register(Subtaste)
class SubtasteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'base_taste']
    list_filter = ['id', 'name', 'base_taste']
    

@admin.register(SubtasteAdditive)
class SubtasteAdditiveAdmin(admin.ModelAdmin):
    list_display = ['id', 'subtaste', 'additive']
    list_filter = ['id', 'subtaste', 'additive']


@admin.register(TasteSubtaste)
class TasteSubtasteAdmin(admin.ModelAdmin):
    list_display = ['id', 'taste', 'subtaste']
    list_filter = ['id', 'taste', 'subtaste']

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'display_additives', 'display_subtastes']
    list_filter = ['id','name']
    
    def display_additives(self, obj):
        additives = obj.additives.all()
        names = [additive.name for additive in additives]
        return ', '.join(names)
    display_additives.short_description = 'Additive'
    
    def display_subtastes(self, obj):
        subtastes = obj.subtastes.all()
        names = [subtaste.name for subtaste in subtastes]
        return ', '.join(names)
    display_subtastes.short_description = 'Subtaste'

@admin.register(Blend)
class BlendAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'subtaste', 'created_at']
