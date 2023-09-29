from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin
from .models import Account , UserProfile
from django.utils.html import format_html
# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name','username','last_login','date_joined', 'is_active')
    list_display_links = ('email', 'first_name','last_name')
    readonly_fields = ('last_login', 'date_joined','password')
    ordering = ('-date_joined',)


    filter_horizontal=()
    list_filter=()
    fieldsets=()

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    
    thumbnail.short_description = "Imagen de perfil"
    list_display =('thumbnail','user','city','state','country')