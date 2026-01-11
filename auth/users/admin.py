from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class StudentInline(admin.StackedInline):
    model = User.student_profile.related.related_model
    can_delete = False
    verbose_name = 'Talaba profili'
    verbose_name_plural = 'Talaba profili'
    extra = 0
    fields = ('group', 'date_of_birth', 'address')


class TeacherInline(admin.StackedInline):
    model = User.teacher_profile.related.related_model
    can_delete = False
    verbose_name = "O'qituvchi profili"
    verbose_name_plural = "O'qituvchi profili"
    extra = 0
    fields = ('subjects', 'experience_years', 'bio')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'user_type', 'is_active', 'phone_verified', 'date_joined')
    list_filter = ('user_type', 'is_active', 'phone_verified', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Shaxsiy ma\'lumotlar'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Foydalanuvchi turi'), {'fields': ('user_type',)}),
        (_('Telegram bot'), {'fields': ('bot_user',)}),
        (_('Ruxsatlar'), {
            'fields': ('is_active', 'phone_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Muhim sanalar'), {'fields': ('date_joined', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'user_type', 'is_active', 'phone_verified'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    filter_horizontal = ('groups', 'user_permissions',)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        
        inlines = []
        if obj.user_type == 'student':
            inlines.append(StudentInline(self.model, self.admin_site))
        elif obj.user_type == 'teacher':
            inlines.append(TeacherInline(self.model, self.admin_site))
        
        return inlines
    
    def get_inlines(self, request, obj):
        if not obj:
            return []
        
        if obj.user_type == 'student':
            return [StudentInline]
        elif obj.user_type == 'teacher':
            return [TeacherInline]
        return []
