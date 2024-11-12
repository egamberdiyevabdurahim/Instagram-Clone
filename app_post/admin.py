from django.contrib import admin

from app_post import models


@admin.register(models.TagModel)
class TagModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'created_at')
    list_display_links = list_display
    search_fields = ('tag', 'id')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(models.MarkModel)
class MarkModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__username', 'created_at')
    list_display_links = list_display
    search_fields = ('user__username',
                     'user__email',
                     'user__phone_number',
                     'post_description',
                     'story_description',
                     'id')
    list_filter = ('user', 'created_at')


@admin.register(models.PostModel)
class PostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__username', 'description', 'created_at')
    list_display_links = list_display
    search_fields = ('user__username',
                     'user__email',
                     'user_phone_number',
                     'description')
    list_filter = ('user', 'created_at', 'is_deleted')
    ordering = ('-created_at',)


@admin.register(models.LikePostModel)
class LikePostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'post__description', 'user__username', 'created_at')
    list_display_links = list_display
    search_fields = ('post__description',
                     'post__user__username',
                     'post__user__email',
                     'post__user_phone_number',
                     'user__username',
                     'user__email',
                     'user__phone_number')
    list_filter = ('post', 'user', 'created_at')
    ordering = ('-created_at',)


@admin.register(models.CommentPostModel)
class CommentPostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'post__description', 'user__username', 'created_at')
    list_display_links = list_display
    search_fields = ('comment',
                     'post__description',
                     'post__user__username',
                     'post__user__email',
                     'post__user_phone_number',
                     'user__username',
                     'user__email',
                     'user__phone_number')
    list_filter = ('post', 'user', 'created_at', 'is_deleted')
    ordering = ('-created_at',)


@admin.register(models.LikeCommentModel)
class LikeCommentModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment__comment', 'user__username', 'created_at')
    list_display_links = list_display
    search_fields = ('comment__comment',
                     'comment__user__username',
                     'comment__user__email',
                     'comment__user__phone_number'
                     'user__username',
                     'user__email',
                     'user__phone_number')
    list_filter = ('comment', 'user', 'created_at')
    ordering = ('-created_at',)


@admin.register(models.StoryModel)
class StoryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__username', 'description', 'created_at', 'is_cached')
    list_display_links = list_display
    search_fields = ('user__username',
                     'user__email',
                     'user__phone_number',
                     'description')
    list_filter = ('user', 'created_at', 'is_deleted', 'is_cached')
    ordering = ('-created_at',)


@admin.register(models.LikeStoryModel)
class LikeStoryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'story__description', 'user__username', 'created_at')
    list_display_links = list_display
    search_fields = ('story__description',
                     'story__user__username',
                     'story__user__email',
                     'story__user_phone_number',
                     'user__username',
                     'user__email',
                     'user__phone_number')
    list_filter = ('story', 'user', 'created_at')
    ordering = ('-created_at',)
