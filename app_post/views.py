from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from app_post import serializers, models
from app_common.permissions import IsOwnerOrReadOnly
from app_user.serializers import UserModel


class PostListView(generics.ListCreateAPIView):
    queryset = models.PostModel.objects.all()
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')
        if q:
            self.queryset = self.queryset.filter(description__icontains=q)

        if tag:
            self.queryset = self.queryset.filter(tags__name=tag)

        return self.queryset


class PostByUserListView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        q = self.request.GET.get('q')
        user_id = self.kwargs.get('user_id')
        tag = self.kwargs.get('tag')

        queryset = models.PostModel.objects.filter(user__id=user_id)

        if not queryset.exists():
            raise NotFound('No posts found for this user.')

        if q:
            queryset = queryset.filter(description__icontains=q)

        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.PostModel.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj


class StoryListView(generics.ListCreateAPIView):
    queryset = models.StoryModel.objects.all()
    serializer_class = serializers.StorySerializer

    def get_queryset(self):
        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')

        if q:
            self.queryset = self.queryset.filter(description__icontains=q)

        if tag:
            self.queryset = self.queryset.filter(tags__name=tag)

        return self.queryset


class StoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.StoryModel.objects.all()
    serializer_class = serializers.StorySerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj


class CommentListView(generics.ListAPIView):
    queryset = models.CommentPostModel.objects.all()
    serializer_class = serializers.CommentPostSerializer

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            self.queryset = self.queryset.filter(comment__icontains=q)

        return self.queryset


class CommentByPostListView(generics.ListCreateAPIView):
    serializer_class = serializers.CommentPostSerializer

    def get_queryset(self):
        q = self.request.GET.get('q')
        post_id = self.kwargs.get('post_id')
        queryset = models.CommentPostModel.objects.filter(post_id=post_id)

        if not queryset.exists():
            raise NotFound('No comments found for this post.')

        if q:
            queryset = queryset.filter(comment__icontains=q)
        return queryset

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = models.PostModel.objects.filter(id=post_id, is_deleted=False)

        if not post.exists():
            self.request.failed_status_code = status.HTTP_404_NOT_FOUND
            raise NotFound("Post not found")

        serializer.save(post_id=post.first().id)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.CommentPostModel.objects.all()
    serializer_class = serializers.CommentPostSerializer
    permission_classes = [IsOwnerOrReadOnly]


class LikePostView(generics.ListCreateAPIView):
    queryset = models.LikePostModel.objects.all()
    serializer_class = serializers.LikePostSerializer

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = models.PostModel.objects.filter(id=post_id, is_deleted=False).first()

        if not post:
            self.request.failed_status_code = status.HTTP_404_NOT_FOUND
            raise NotFound("Post not found")

        like = self.queryset.filter(user=self.request.user, post=post)

        if like.exists():
            like.delete()
            return Response({'message': 'Unliked Successfully'}, status=status.HTTP_200_OK)

        serializer.save(user_id=self.request.user.pk, post_id=post.id)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeStoryView(generics.ListCreateAPIView):
    queryset = models.LikeStoryModel.objects.all()
    serializer_class = serializers.LikeStorySerializer

    def perform_create(self, serializer):
        story_id = self.kwargs.get('story_id')
        story = models.StoryModel.objects.filter(id=story_id, is_deleted=False)

        if not story.exists():
            self.request.failed_status_code = status.HTTP_404_NOT_FOUND
            raise NotFound("Story not found")

        like = self.queryset.filter(user=self.request.user, story=story.first())

        if like.exists():
            like.delete()
            return Response({'message': 'Unliked Successfully'}, status=status.HTTP_200_OK)

        serializer.save(story_id=story.first().id)
        return Response(serializer.data, status.HTTP_200_OK)


class LikeCommentView(generics.ListCreateAPIView):
    queryset = models.LikeCommentModel.objects.all()
    serializer_class = serializers.LikeCommentSerializer

    def perform_create(self, serializer):
        comment_id = self.kwargs.get('comment_id')
        comment = models.CommentPostModel.objects.filter(id=comment_id, is_deleted=False)

        if not comment.exists():
            self.request.failed_status_code = status.HTTP_404_NOT_FOUND
            raise NotFound("Comment not found")

        comment = comment.first()

        like = self.queryset.filter(user=self.request.user, comment=comment)

        if like.exists():
            like.delete()
            return Response({'message': 'Unliked Successfully'}, status=status.HTTP_200_OK)

        serializer.save(comment_id=comment.pk)
        return Response(serializer.data, status.HTTP_200_OK)


class TagListView(generics.ListAPIView):
    queryset = models.TagModel.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            self.queryset = self.queryset.filter(tag__icontains=q)

        return self.queryset


class TagDetailView(generics.RetrieveAPIView):
    queryset = models.TagModel.objects.all()
    serializer_class = serializers.TagSerializer


class TopPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        queryset = models.PostModel.objects.filter(views__gt=1).order_by('-views')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(title__icontains=q)

        return queryset


class ConnectUserToPostView(APIView):
    serializer_class = serializers.ConnectUsersToPostSerializer

    def post(self, request, post_id):
        post = models.PostModel.objects.filter(pk=post_id, is_deleted=False)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not post.exists():
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        post = post.first()
        user = UserModel.objects.filter(pk=serializer.validated_data.get('user_id')).first()

        if user in post.connected_users.all():
            post.connected_users.remove(user)
            return Response({'error': 'User unconnected from the post successfully'}, status=status.HTTP_200_OK)

        post.connected_users.add(user)
        post.save()
        return Response({'message': 'User connected to the post successfully'}, status=status.HTTP_200_OK)
