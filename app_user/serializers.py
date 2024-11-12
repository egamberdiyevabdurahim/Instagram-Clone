from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import serializers

from app_common.views import email_validator
from app_post.models import MarkModel
from app_user.models import VerifyCodeModel, FollowModel

UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username_or_email_or_phone_number = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(max_length=64, required=True)

    def validate(self, attrs):
        username_or_email_or_phone_number: str = attrs.get('username_or_email_or_phone_number').strip().lower()

        if email_validator(username_or_email_or_phone_number):
            user = UserModel.objects.filter(email=username_or_email_or_phone_number)
            if not user.exists():
                raise serializers.ValidationError("Gmail or Password invalid!")

        elif (username_or_email_or_phone_number.startswith('+')
              and username_or_email_or_phone_number[1:].isnumeric()):

            if not username_or_email_or_phone_number.startswith('+998'):
                raise serializers.ValidationError("Phone number must start with +998")

            user = UserModel.objects.filter(phone_number=username_or_email_or_phone_number)
            if not user.exists():
                raise serializers.ValidationError("Phone number or Password invalid!")

        else:
            user = UserModel.objects.filter(username=username_or_email_or_phone_number)
            if not user.exists():
                raise serializers.ValidationError("Username or Password invalid!")

        if not user.first().is_active:
            raise serializers.ValidationError("User is not active")

        attrs['user'] = user.first()

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=64, required=True, write_only=True)

    class Meta:
        model = UserModel
        fields = ('username', 'email', 'phone_number', 'password', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        username = attrs.get('username').strip().lower()
        email = attrs.get('email').strip()
        phone_number: str = attrs.get('phone_number').strip().lower()
        password = attrs.get('password').strip()
        confirm_password = attrs.get('confirm_password').strip()

        if not username:
            raise serializers.ValidationError("Username is required")

        if not email_validator(email):
            raise serializers.ValidationError("Invalid email address email must be gmail")

        if not phone_number.startswith('+998') and not phone_number[1:].isnumeric():
            raise serializers.ValidationError("Phone number must start with +998 and contain only digits after the country code")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        user = UserModel.objects.filter(username=username).first()
        if user:
            raise serializers.ValidationError("Username already exists")

        user = UserModel.objects.filter(email=email).first()
        if user:
            raise serializers.ValidationError("Email already exists")

        user = UserModel.objects.filter(phone_number=phone_number).first()
        if user:
            raise serializers.ValidationError("Phone number already exists")

        return attrs

    def create(self, validated_data: list):
        validated_data.pop('confirm_password')
        user = UserModel(
            username=validated_data['username'].lower(),
            email=validated_data['email'].lower(),
            phone_number=validated_data['phone_number'].lower(),
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'phone_number', 'first_name', 'last_name')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request_user = self.context['request'].user

        if request_user != instance:
            data['is_following'] = FollowModel.objects.filter(
                follower_id=request_user.id, followed=instance
            ).exists()
        else:
            data['comments_count'] = instance.comments_count
            data['likes_count'] = instance.likes_count
            data['story_likes_count'] = instance.story_likes_count
            data['comment_likes_count'] = instance.comment_likes_count

        data['followers_count'] = instance.followers_count
        data['following_count'] = instance.following_count
        data['posts_count'] = instance.posts_count
        data['stories_count'] = instance.stories_count

        data['followers'] = [
            {
                'id': follower.pk,
                'user_id': follower.follower.pk,
                'username': follower.follower.username,
                'is_i_follow': True if FollowModel.objects.filter(followed__pk=follower.pk, follower__pk=instance.pk).exists() else False
            }
            for follower in instance.followers.all()
        ]
        data['following'] = [
            {
                'id': following.pk,
                'user_id': following.followed.pk,
                'username': following.followed.username,
                'is_followed': True if FollowModel.objects.filter(followed__pk=instance.pk, follower__pk=instance.pk).exists() else False
            }
            for following in instance.following.all()
        ]
        data['posts'] = [
            {
                'id': post.pk,
                'description': post.description[:33]
            }
            for post in instance.posts.all()
        ]
        data['stories'] = [
            {
                'id': story.pk,
                'description': story.description[:33]
            }
            for story in instance.stories.all()
        ]
        data['comments'] = [
            {
                'id': comment.pk,
                'post_id': comment.post.pk,
                'post_description': comment.post.description[:33],
                'comment': comment.comment[:33]
            }
            for comment in instance.comments.all()
        ]

        data['marks_count'] = instance.marks_count
        data['marks'] = [
            {
                'id': mark.pk,
                'post_id': mark.post.pk if mark.post else None,
                'post_description': mark.post.description[:33] if mark.post else None,
                'story_id': mark.story.pk if mark.story else None,
                'story_description': mark.story.description[:33] if mark.story else None
            }
            for mark in instance.marks.all()
        ]

        return data


class VerifyCodeSerializer(serializers.Serializer):
    email_or_phone_number = serializers.CharField(max_length=64, required=True)
    code = serializers.CharField(max_length=4, required=True)

    def validate(self, attrs):
        email_or_phone_number = attrs.get('email_or_phone_number')
        code = attrs.get('code')

        user = None
        verify_code = None
        type_code = None
        if email_validator(email_or_phone_number):
            user = UserModel.objects.filter(email=email_or_phone_number).first()
            verify_code = VerifyCodeModel.objects.filter(user=user, code_email=code).first()
            type_code = 'email'

        elif (email_or_phone_number.startswith('+998')
              and email_or_phone_number[1:].isnumeric()):
            user = UserModel.objects.filter(phone_number=email_or_phone_number).first()
            verify_code = VerifyCodeModel.objects.filter(user=user, code_sms=code).first()
            type_code ='sms'

        if not verify_code:
            raise serializers.ValidationError("Invalid confirmation code")

        if type_code == 'email':
            if verify_code.created_at + timedelta(minutes=3) < timezone.now():
                raise serializers.ValidationError("Confirmation code has expired\nPlease resend your confirmation code")

        if type_code == 'sms':
            if verify_code.created_at + timedelta(minutes=5) < timezone.now():
                raise serializers.ValidationError("Confirmation code has expired\nPlease resend your confirmation code")

        verify_code.delete()

        attrs['user'] = user

        return attrs


class ResendConfirmationSerializer(serializers.Serializer):
    email_or_phone_number = serializers.CharField(max_length=64, required=True)

    def validate(self, attrs):
        email_or_phone_number = attrs.get('email_or_phone_number')

        user = None
        if email_validator(email_or_phone_number):
            user = UserModel.objects.filter(email=email_or_phone_number).first()

        elif (email_or_phone_number.startswith('+998')
              and email_or_phone_number[1:].isnumeric()):
            user = UserModel.objects.filter(phone_number=email_or_phone_number).first()

        if not user:
            raise serializers.ValidationError("Email/Phone number is not valid!")

        if user.is_active:
            raise serializers.ValidationError("User is already active!")

        attrs['user'] = user

        return attrs


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowModel
        fields = ['follower', 'followed']
        read_only_fields = ['follower', 'followed']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, FollowModel):
            data['follower'] = {
                'id': instance.follower.pk,
                'username': instance.follower.username,
                'email': instance.follower.email,
                'phone_number': instance.follower.phone_number,
            }
            data['followed'] = {
                'id': instance.followed.pk,
                'username': instance.followed.username,
                'email': instance.followed.email,
            }
        return data


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkModel
        fields = ['user', 'post', 'story']
        read_only_fields = ['user', 'post', 'story']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['data'] = [
            {
                'user_id': instance.user.pk,
                'user_username': instance.user.username,
                'user_email': instance.user.email,
                'post_id': instance.post.pk if instance.post else None,
                'post_description': instance.post.description[:33] if instance.post else None,
                'story_id': instance.story.pk if instance.story else None,
                'story_description': instance.story.description[:33] if instance.story else None,
            }
        ]
        return data
