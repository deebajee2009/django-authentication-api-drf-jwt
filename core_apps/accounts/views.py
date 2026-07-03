"""
Accounts app views.
"""
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .serializers import ( UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserChangePasswordSerializer, SentResetPasswordEmailSerializer, UserPasswordResetSerializer
)
from .renderers import UserRenderer
from .tasks import send_welcome_email, send_reset_password_email


def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_welcome_email.delay(user.id)
            token = get_tokens_for_user(user)
            return Response(
                {
                    'token': token,
                    'message': 'You are register successfully',
                    'user': serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Alternative
# from rest_framework.generics import CreateAPIView

# class UserRegistrationView(CreateAPIView):
#     serializer_class = UserRegistrationSerializer


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'token': token, 'message': 'Login successful'}, status=status.HTTP_200_OK)
            return Response({'errors': 'Password or Email is not valid'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class SentResetPasswordEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = SentResetPasswordEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = serializer.link
        user_id = serializer.user_id
        send_reset_password_email.delay(user_id, link)

        return Response({'message': 'Password reset link sent, click on the link.'})


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, uid, token, request):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Password Reset Successfully.'}, status=status.HTTP_200_OK)


class LogoutUserView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token_object = RefreshToken(refresh_token)
            token_object.blacklist()

            return Response({'message': 'You logout successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'message': f'Token error occured: {e}'}, status=status.HTTP_400_BAD_REQUEST)