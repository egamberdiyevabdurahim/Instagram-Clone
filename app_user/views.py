import random
import string

from threading import Thread
from twilio.rest import Client

from django.core.mail import send_mail

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from conf import settings
from app_user import serializers, models
from app_common.permissions import IsItsOrReadOnly


def randomer(code):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=code))


def send_confirmation(user):
    code_email = randomer(4)
    code_sms = randomer(4)

    if models.VerifyCodeModel.objects.filter(user=user).exists():
        models.VerifyCodeModel.objects.filter(user=user).delete()

    models.VerifyCodeModel.objects.create(
        user=user,
        code_email=code_email,
        code_sms=code_sms
    )
    send_mail(
        subject="Email Confirmation",
        message=f"Your confirmation code is: {code_email}\n"
                f"It expires in 3 minutes!",
        from_email=f"{settings.EMAIL_HOST_USER}",
        recipient_list=[user.email],
    )
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        from_=settings.TWILIO_PHONE_NUMBER,
        body=f"Your confirmation code is: {code_sms}\n"
             f"It expires in 3 minutes!\n"
             f"Made By MasterPhone",
        to=settings.TWILIO_RECEIVING_PHONE
    )
    return code_email, code_sms


class ResendEmailConfirmation(generics.CreateAPIView):
    serializer_class = serializers.ResendConfirmationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')

        Thread(target=send_confirmation, args=(user,)).start()

        response_data = {
            'message': (
                f'Confirmation code sent to {user.email}. It expires in 3 minutes\n'
                f'Confirmation code sent to {user.phone_number}. It expires in 5 minutes\n'
                f'Enter one of these'
            )
        }

        return Response(response_data, status=status.HTTP_200_OK)


class VerifyEmailConfirmation(generics.CreateAPIView):
    serializer_class = serializers.VerifyCodeSerializer
    permission_classes = [AllowAny]
    response_data = None

    def perform_create(self, serializer):
        user = serializer.validated_data.get('user')
        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)

        self.response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
        }
        return self

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(self.response_data, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = [AllowAny]
    user = None

    def perform_create(self, serializer):
        self.user = serializer.save()
        return self

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)

        response_data = {
            'message': (
                f'Confirmation code sent to {self.user.email}. It expires in 3 minutes\n'
                f'Confirmation code sent to {self.user.phone_number}. It expires in 5 minutes\n'
                f'Enter one of these'
            )
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = [AllowAny]
    refresh_token = None
    user = None

    def perform_create(self, serializer):
        user = serializer.validated_data.get('user')

        self.refresh_token = RefreshToken.for_user(user)
        self.user = user

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)

        return Response({
            'refresh': str(self.refresh_token),
            'access': str(self.refresh_token.access_token),
            'username': self.user.username,
            'email': self.user.email,
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ProfileSerializer
    queryset = models.UserModel.objects.all()
    permission_classes = [IsItsOrReadOnly]


class FollowListView(generics.ListCreateAPIView):
    queryset = models.FollowModel.objects.all()
    serializer_class = serializers.FollowSerializer

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        user = models.UserModel.objects.filter(id=user_id, is_deleted=False).first()

        if not user:
            self.request.failed_status_code = status.HTTP_404_NOT_FOUND
            raise NotFound("User not found")

        if user == self.request.user:
            self.request.failed_status_code = status.HTTP_403_FORBIDDEN
            raise PermissionDenied("You can't follow yourself")

        follow = self.queryset.filter(follower=self.request.user, followed=user)

        if follow.exists():
            follow.delete()
            return Response({'message': 'Unfollowed'}, status=status.HTTP_200_OK)

        serializer.save(follower=self.request.user, followed_id=user.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class FollowersListView(generics.ListAPIView):
    serializer_class = serializers.FollowSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return models.FollowModel.objects.filter(followed=user_id)


class FollowingListView(generics.ListAPIView):
    serializer_class = serializers.FollowSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return models.FollowModel.objects.filter(follower=user_id)
