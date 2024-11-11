from django.contrib import admin

from app_user.models import UserModel, FollowModel, VerifyCodeModel

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone_number')
    list_display_links = list_display
    search_fields = ('id', 'username', 'email', 'phone_number')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-date_joined',)


@admin.register(FollowModel)
class FollowModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed', 'created_at')
    list_display_links = list_display
    search_fields = ('id',
                     'follower__username',
                     'follower__email',
                     'follower__phone_number',
                     'followed__email',
                     'followed__username',
                     'followed__phone_number')
    list_filter = ('follower', 'followed', 'created_at')
    ordering = ('-created_at',)


@admin.register(VerifyCodeModel)
class VerifyCodeModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__username', 'code_email', 'code_sms', 'created_at')
    list_display_links = list_display
    search_fields = ('id',
                     'user__username',
                     'user__email',
                     'user__phone_number',
                     'code_email',
                     'code_sms')
    list_filter = ('user', 'created_at')
    ordering = ('-created_at',)
