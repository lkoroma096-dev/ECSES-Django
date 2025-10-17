from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, Message, Notification

# Unregister the default User admin
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Enhanced User admin with role-based management"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'userprofile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('userprofile',)
        }),
    )
    
    def get_role(self, obj):
        if hasattr(obj, 'userprofile'):
            role_colors = {
                'admin': 'danger',
                'teacher': 'primary',
                'parent': 'success',
                'child': 'warning'
            }
            color = role_colors.get(obj.userprofile.role, 'secondary')
            return format_html(
                '<span class="badge bg-{}">{}</span>',
                color,
                obj.userprofile.get_role_display()
            )
        return 'No Role'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'userprofile__role'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile admin with role-based features"""
    list_display = ('user', 'role', 'phone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'date_of_birth')
        }),
        ('Profile', {
            'fields': ('profile_picture',)
        }),
        ('Role-Specific Information', {
            'fields': ('teacher_id', 'parent_children', 'teacher_children'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('parent_children', 'teacher_children')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin for communication management"""
    list_display = ('subject', 'sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'sender__userprofile__role', 'recipient__userprofile__role')
    search_fields = ('subject', 'content', 'sender__username', 'recipient__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'recipient', 'subject', 'content')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Threading', {
            'fields': ('parent_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'recipient')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin for system alerts"""
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at', 'user__userprofile__role')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read', 'expires_at')
        }),
        ('Additional', {
            'fields': ('related_url',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Customize admin site
admin.site.site_header = "ECSES Administration"
admin.site.site_title = "ECSES Admin"
admin.site.index_title = "Early Support in Childhood Educational System"