from django.contrib import admin
from django.utils.html import format_html
from .models import BotUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name_display', 'username_display', 'phone_number', 'linked_user', 'is_active', 'last_interaction')
    list_filter = ('is_active', 'is_bot', 'language_code', 'created_at', 'last_interaction')
    search_fields = ('user_id', 'first_name', 'last_name', 'username', 'phone_number')
    readonly_fields = ('user_id', 'created_at', 'updated_at', 'last_interaction')
    ordering = ('-last_interaction',)
    
    fieldsets = (
        ('Telegram ma\'lumotlari', {
            'fields': ('user_id', 'first_name', 'last_name', 'username', 'language_code')
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('phone_number',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_bot')
        }),
        ('Sanalar', {
            'fields': ('created_at', 'updated_at', 'last_interaction'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name_display(self, obj):
        """Ism va familyani birlashtiradi"""
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full_name if full_name else "-"
    full_name_display.short_description = "To'liq ism"
    
    def username_display(self, obj):
        """Username ni @ bilan ko'rsatadi"""
        if obj.username:
            return format_html('<a href="https://t.me/{}" target="_blank">@{}</a>', obj.username, obj.username)
        return "-"
    username_display.short_description = "Username"
    
    def linked_user(self, obj):
        """Bog'langan User ni ko'rsatadi"""
        try:
            from auth.users.models import User
            user = User.objects.filter(bot_user=obj).first()
            if user:
                return format_html('<a href="/admin/users/user/{}/change/">{}</a>', user.id, user.phone_number)
            return format_html('<span style="color: red;">Bog\'lanmagan</span>')
        except Exception:
            return "-"
    linked_user.short_description = "Bog'langan User"
    
    def has_add_permission(self, request):
        """BotUser qo'shish ruxsatini o'chirish (faqat bot orqali yaratilishi kerak)"""
        return False
