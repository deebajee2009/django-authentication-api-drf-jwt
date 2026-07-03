"""
Accounts app serializers.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password & Confirm Password do not match")

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name"]


class UserChangePasswordSerializer(serializers.SerializerSerializer):
    password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        max_length=255,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                "Password and Confirm Password do not match."
            )

        return attrs

    def save(self, **kwargs):
        user = self.context["user"]

        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])

        return user


class SentResetPasswordEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/reset/'+uid+'/'+token
            self.link = link
            self.user_id = user.id

            return attrs
        else:
            raise serializers.ValidationError("You are not registered.")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        max_length=255,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        try :
            if attrs["password"] != attrs["password2"]:
                raise serializers.ValidationError(
                    "Password and Confirm Password do not match."
                )

            uid = self.context.get('uid')
            token = self.context.get('token')

            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is expired or invalid')

            self.user = user

            return attrs
        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError('Token is expired or invalid')

    def save(self, **kwargs):
        self.user.set_password(self.validated_data["password"])
        self.user.save(update_fields=["password"])

        return self.user