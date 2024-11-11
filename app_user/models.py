from django.db import models
from django.contrib.auth.models import AbstractUser


class UserModel(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=14, unique=True)
    avatar = models.ImageField(upload_to='User/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}/{self.email}/{self.phone_number}"

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def posts_count(self):
        return self.posts.count()

    @property
    def stories_count(self):
        return self.stories.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def story_likes_count(self):
        return self.story_likes.count()

    @property
    def comment_likes_count(self):
        return self.comment_likes.count()


class FollowModel(models.Model):
    follower = models.ForeignKey(UserModel, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(UserModel, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        verbose_name = "FollowModel"
        verbose_name_plural = "Follows"

    def __str__(self):
        return f"{self.follower} follows {self.followed}"


class VerifyCodeModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    code_email = models.CharField(max_length=4)
    code_sms = models.CharField(max_length=4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code_email}/{self.code_sms}"

    class Meta:
        verbose_name = "Verify Code"
        verbose_name_plural = "Verify Codes"
