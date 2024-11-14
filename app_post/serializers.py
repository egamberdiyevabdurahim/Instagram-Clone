from django.contrib.auth import get_user_model

from rest_framework import serializers

from app_post import models

UserModel = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TagModel
        fields = ['id', 'tag']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['posts_count'] = instance.posts_count
        data['stories_count'] = instance.stories_count

        if instance.posts:
            data['posts'] = [
                {
                    'id': post.pk,
                    'description': post.description[:33]
                }
                for post in instance.posts.all()
            ]

        else:
            data['stories'] = [
                {
                    'id': story.pk,
                    'description': story.description[:33]
                }
                for story in instance.stories.all()
            ]

        return data


class MarkSerializer(serializers.ModelSerializer):
    post = serializers.CharField(max_length=64, required=False)
    story = serializers.CharField(max_length=64, required=False)

    class Meta:
        model = models.MarkModel
        fields = ['id', 'user', 'post', 'story']

    def validate(self, attrs):
        post_id = attrs.pop('post')
        story_id = attrs.pop('story')

        if post_id and models.PostModel.objects.filter(id=post_id, is_deleted=False).exists():
            attrs['post'] = post_id

        if story_id and models.StoryModel.objects.filter(id=story_id, is_deleted=False).exists():
            attrs['story'] = story_id

        if not story_id and not post_id:
            raise serializers.ValidationError("Either post or story must be provided.")

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.post:
            data['user'] = {
                'id': instance.post.pk,
                'username': instance.user.username
            }
            data['post'] = {
                'id': instance.post.pk,
                'description': instance.post.description[:33]
            }

        if instance.story:
            data['story'] = {
                'id': instance.story.pk,
                'description': instance.story.description[:33]
            }

        return data


class PostSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    videos = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)

    class Meta:
        model = models.PostModel
        fields = ['id', 'photos', 'videos', 'description', 'user', 'tags', 'views']
        read_only_fields = ['user', 'tags', 'views']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = {
            'id': instance.user.pk,
            'username': instance.user.username,
            'email': instance.user.email,
            'phone_number': instance.user.phone_number
        }

        if instance.user.is_private is False:
            data['connected_users'] = [
                {'id': user.pk, 'username': user.username} if user else None
                for user in instance.connected_users.all()
            ]
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

            data['tags_count'] = instance.tags_count
            data['tags'] = [
                {
                    'id': tag.pk,
                    'tag': tag.tag
                }
                for tag in instance.tags.all()
            ]

            data['marks_count'] = instance.marks_count
            data['marks'] = [
                {
                    'id': mark.pk,
                    'user': {
                        'id': mark.user.pk,
                        'username': mark.user.username
                    }
                }
                for mark in instance.marks.all()
            ]

            data['photos'] = [{'id': photo.pk, 'url': photo.photo.url} for photo in instance.photos.all()]
            data['videos'] = [{'id': video.pk, 'url': video.video.url} for video in instance.videos.all()]

        else:
            data['message'] = "This Video is uploaded by private account"

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])
        description = validated_data.get('description').split(' ')

        tags = [tag for tag in description if tag.startswith('#')]
        marks = [mark.lower() for mark in description
                 if mark.startswith('@') and UserModel.objects.filter(username=mark[1:].lower()).exists()]

        if not videos_data and not photos_data:
            raise serializers.ValidationError('Either photos or videos are required')

        post = models.PostModel.objects.create(user=user, **validated_data)

        for photo_data in photos_data:
            photo = models.PhotoModel.objects.create(photo=photo_data)
            post.photos.add(photo)

        for video_data in videos_data:
            video = models.VideoModel.objects.create(video=video_data)
            post.videos.add(video)

        for tag in tags:
            tag_instance, _ = models.TagModel.objects.get_or_create(tag=tag)
            post.tags.add(tag_instance)

        for mark in marks:
            if mark:
                mark_instance, _ = models.MarkModel.objects.get_or_create(user_id=user.pk, post_id=post.pk)

        return post



class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoryModel
        fields = ['id', 'photo', 'video', 'description', 'user', 'tags']
        read_only_fields = ['user', 'tags']

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

        if instance.user.is_private is False:
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

            data['tags_count'] = instance.tags_count
            data['tags'] = [
                {
                    'id': tag.pk,
                    'tag': tag.tag
                }
                for tag in instance.tags.all()
            ]

            data['marks_count'] = instance.marks_count
            data['marks'] = [
                {
                    'id': mark.pk,
                    'user': {
                        'id': mark.user.pk,
                        'username': mark.user.username
                    }
                }
                for mark in instance.marks.all()
            ]

        else:
            data['message'] = "This Video is uploaded by private account"

        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        description = validated_data.get('description').split(' ')

        story = models.StoryModel.objects.create(user=user, **validated_data)

        tags = [tag for tag in description if tag.startswith('#')]
        marks = [mark.lower() for mark in description
                 if mark.startswith('@') and UserModel.objects.filter(username=mark[1:].lower()).exists()]

        for tag in tags:
            tag_instance, _ = models.TagModel.objects.get_or_create(tag=tag)
            story.tags.add(tag_instance)

        for mark in marks:
            if mark:
                mark_instance, _ = models.MarkModel.objects.get_or_create(user_id=user.pk, story_id=story.pk)

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

        if instance.post.user.is_private is False:
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

        else:
            data['message'] = "This Video is uploaded by private account"

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

            if instance.post.user.is_private is False:
                data['post'] = {'id': instance.post.pk,
                                'description': instance.post.description[:33],
                                'user': {'id': instance.post.user.pk,
                                         'username': instance.post.user.username,
                                         'email': instance.post.user.email,
                                         'phone_number': instance.post.user.phone_number}
                                }

            else:
                data['message'] = "This Video is uploaded by private account"
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

            if instance.story.user.is_private is False:
                data['story'] = {'id': instance.story.pk,
                                 'description': instance.story.description,
                                 'user': {'id': instance.user.pk,
                                          'username': instance.user.username,
                                          'email': instance.user.email,
                                          'phone_number': instance.user.phone_number}
                                 }

            else:
                data['message'] = "This Story is uploaded by private account"
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


class ConnectUsersToPostSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def validate_user_id(self, value):
        if not UserModel.objects.filter(pk=value).exists():
            raise serializers.ValidationError("User not found.")

        return value