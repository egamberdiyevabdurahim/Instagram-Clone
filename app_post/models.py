from django.db import models

from app_common.models import BaseModel
from app_user.models import UserModel


class PhotoModel(models.Model):
    photo = models.ImageField(upload_to='Post/Photos/')

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self):
        return self.photo.name


class VideoModel(models.Model):
    video = models.FileField(upload_to='Post/Videos/')

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.video.name


class TagModel(BaseModel):
    tag = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.tag

    @property
    def posts_count(self):
        return self.posts.count()

    @property
    def stories_count(self):
        return self.stories.count()


class PostModel(BaseModel):
    description = models.TextField()
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, related_name='posts')
    connected_users = models.ManyToManyField(UserModel, related_name='connected_posts')
    photos = models.ManyToManyField(PhotoModel, related_name='posts')
    videos = models.ManyToManyField(VideoModel, related_name='posts')
    tags = models.ManyToManyField(TagModel, related_name='posts')
    views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f"{self.user.username}/{self.description}"

    @property
    def photos_count(self):
        return self.photos.count()

    @property
    def videos_count(self):
        return self.videos.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def tags_count(self):
        return self.tags.count()

    @property
    def marks_count(self):
        return self.marks.count()


class StoryModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, related_name='stories')
    photo = models.ImageField(upload_to='Story/Photos/', null=True, blank=True)
    video = models.FileField(upload_to='Story/Videos/', null=True, blank=True)
    tags = models.ManyToManyField(TagModel, related_name='stories')
    description = models.TextField()
    is_cached = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f"{self.user.username}/{self.description[:10]}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def tags_count(self):
        return self.tags.count()

    @property
    def marks_count(self):
        return self.marks.count()


class MarkModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='marks')
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='marks', null=True, blank=True)
    story = models.ForeignKey(StoryModel, on_delete=models.CASCADE, related_name='marks', null=True, blank=True)

    class Meta:
        verbose_name = 'Mark'
        verbose_name_plural = 'Marks'

    def __str__(self):
        return f"{self.user.username}/{self.post.description[:10]}" \
            if self.post else f"{self.user.username}/{self.story.description[:10]}"


class CommentPostModel(BaseModel):
    comment = models.TextField()
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        verbose_name = 'Comment Post'
        verbose_name_plural = 'Comments Post'

    def __str__(self):
        return f"{self.comment}/{self.user.username}"

    @property
    def likes_count(self):
        return self.likes.count()


class LikePostModel(BaseModel):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        verbose_name = 'Like Post'
        verbose_name_plural = 'Likes Post'

    def __str__(self):
        return f"{self.user.username}/{self.post.description[:10]}"


class LikeStoryModel(BaseModel):
    story = models.ForeignKey(StoryModel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='story_likes')

    class Meta:
        verbose_name = 'Like Story'
        verbose_name_plural = 'Likes Story'

    def __str__(self):
        return f'{self.user.username}/{self.story.description[:10]}'


class LikeCommentModel(BaseModel):
    comment = models.ForeignKey(CommentPostModel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        verbose_name = 'Like Comment'
        verbose_name_plural = 'Like Comments'

    def __str__(self):
        return f'{self.user.username}/{self.comment.comment[:10]}'
