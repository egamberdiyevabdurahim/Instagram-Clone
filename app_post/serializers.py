import json

from rest_framework import serializers

from app_post import models


class PostSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)
    videos = serializers.ListField(child=serializers.FileField(), write_only=True)

    class Meta:
        model = models.PostModel
        fields = ['id', 'photos', 'videos', 'description', 'user']
        read_only_fields = ['user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = {
            'id': instance.user.pk,
            'username': instance.user.username,
            'email': instance.user.email,
            'phone_number': instance.user.phone_number
        }

        user = self.context['request'].user
        data['is_liked'] = instance.likes.filter(user=user).exists()

        data['total_likes'] = instance.likes_count
        data['likes'] = [
            {'id': like.pk, 'user': {'id': like.user.pk, 'username': like.user.username}}
            for like in instance.likes.all()
        ]

        data['total_comments'] = instance.comments_count
        data['comments'] = [{
            'id': comment.pk,
            'user': {
                'id': comment.user.pk,
                'username': comment.user.username
            },
            'comment': comment.comment}
            for comment in instance.comments.all()
        ]

        data['photos'] = [{'id': photo.pk, 'url': photo.photo.url} for photo in instance.photos.all()]
        data['videos'] = [{'id': video.pk, 'url': video.video.url} for video in instance.videos.all()]

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])

        post = models.PostModel.objects.create(user=user, **validated_data)

        for photo_data in photos_data:
            photo = models.PhotoModel.objects.create(photo=photo_data)
            post.photos.add(photo)

        for video_data in videos_data:
            video = models.VideoModel.objects.create(video=video_data)
            post.videos.add(video)

        return post



class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoryModel
        fields = ['id', 'photo', 'video', 'description', 'user']
        read_only_fields = ['user']

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            if not 'photo' in attrs and not 'video' in attrs:
                raise serializers.ValidationError('Either photo or video is required')
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = {'id': instance.user.pk,
                        'username': instance.user.username,
                        'email': instance.user.email,
                        'phone_number': instance.user.phone_number}
        user = self.context['request'].user
        if user.is_authenticated:
            data['is_liked'] = instance.likes.filter(user=user).exists()

        else:
            data['is_liked'] = False

        data['total_likes'] = instance.likes_count
        data['likes'] = []
        if instance.likes.exists():
            for likes in instance.likes.all():
                data['likes'].append({'id': likes.pk,
                                      'user': {'id': likes.user.pk,
                                               'username': likes.user.username}
                                      })
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        story = models.StoryModel.objects.create(user=user, **validated_data)
        return story


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CommentPostModel
        fields = ['id', 'comment', 'post', 'user']
        read_only_fields = ['user', 'post']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = {'id': instance.user.pk,
                        'username': instance.user.username,
                        'email': instance.user.email,
                        'phone_number': instance.user.phone_number}
        user = self.context['request'].user
        if user.is_authenticated:
            data['is_liked'] = instance.likes.filter(user=user).exists()

        else:
            data['is_liked'] = False

        data['total_likes'] = instance.likes_count
        data['likes'] = []
        if instance.likes.exists():
            for likes in instance.likes.all():
                data['likes'].append({'id': likes.pk,
                                      'user': {'id': likes.user.pk,
                                               'username': likes.user.username}
                                      })
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        comment = models.CommentPostModel.objects.create(user=user, **validated_data)
        return comment


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LikePostModel
        fields = ['id', 'post', 'user']
        read_only_fields = ['user', 'post']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, models.LikePostModel):
            data['user'] = {'id': instance.user.pk,
                            'username': instance.user.username,
                            'email': instance.user.email,
                            'phone_number': instance.user.phone_number}
            data['post'] = {'id': instance.post.pk,
                            'description': instance.post.description[:33],
                            'user': {'id': instance.post.user.pk,
                                     'username': instance.post.user.username,
                                     'email': instance.post.user.email,
                                     'phone_number': instance.post.user.phone_number}
                            }
        return data


    
    def create(self, validated_data):
        user = self.context['request'].user
        like = models.LikePostModel.objects.create(**validated_data)
        return like


class LikeStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LikeStoryModel
        fields = ['id', 'story', 'user']
        read_only_fields = ['user', 'story']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, models.LikeStoryModel):
            data['user'] = {'id': instance.user.pk,
                            'username': instance.user.username,
                            'email': instance.user.email,
                            'phone_number': instance.user.phone_number}
            data['story'] = {'id': instance.story.pk,
                             'description': instance.story.description,
                             'user': {'id': instance.user.pk,
                                      'username': instance.user.username,
                                      'email': instance.user.email,
                                      'phone_number': instance.user.phone_number}
                             }
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        like = models.LikeStoryModel.objects.create(user_id=user.pk, **validated_data)
        return like


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LikeCommentModel
        fields = ['id', 'user', 'comment']
        read_only_fields = ['user', 'comment']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, models.LikeCommentModel):
            data['user'] = {'id': instance.user.pk,
                            'username': instance.user.username,
                            'email': instance.user.email,
                            'phone_number': instance.user.phone_number}
            data['comment'] = {'id': instance.comment.pk,
                               'comment': instance.comment.comment,
                               'user': {'id': instance.user.pk,
                                        'username': instance.user.username,
                                        'email': instance.user.email,
                                        'phone_number': instance.user.phone_number}
                               }
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        like = models.LikeCommentModel.objects.create(user=user, **validated_data)
        return like
