import uuid
from datetime import timedelta

import jwt
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from .models import RefreshToken
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
)

ERROR_MESSAGES = {
    "invalid_credentials": "Invalid credentials",
    "no_token": "No token provided",
}


@swagger_auto_schema(
    method="post",
    request_body=UserRegistrationSerializer,
    responses={201: UserSerializer, 400: "Bad Request"},
)
@api_view(["POST"])
def register(request):
    """
    Register a new user.

    Parameters:
        - email (string): User's email address (required)
        - password (string): User's password (required)

    Returns:
        - id (integer): User ID
        - email (string): User's email address

    Responses:
        - 201: User created successfully
        - 400: Bad request (validation errors)
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=LoginSerializer,
    responses={
        200: UserSerializer,
        401: "Unauthorized",
        400: "Bad Request",
    },
)
@api_view(["POST"])
def login(request):
    """
    Authenticate user and return tokens.

    Parameters:
        - email (string): User's email address (required)
        - password (string): User's password (required)

    Returns:
        - access_token (string): JWT access token
        - refresh_token (string): UUID refresh token

    Responses:
        - 200: Tokens returned successfully
        - 401: Invalid credentials
        - 400: Bad request (validation errors)
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": ERROR_MESSAGES["invalid_credentials"]},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=RefreshTokenSerializer,
    responses={200: UserSerializer, 401: "Unauthorized", 400: "Bad Request"},
)
@api_view(["POST"])
def refresh(request):
    """
    Refresh access token using refresh token.

    Parameters:
        - refresh_token (string): UUID refresh token (required)

    Returns:
        - access_token (string): New JWT access token
        - refresh_token (string): New UUID refresh token

    Responses:
        - 200: Tokens returned successfully
        - 401: Invalid refresh token
        - 400: Bad request (validation errors)
    """
    serializer = RefreshTokenSerializer(data=request.data)
    if serializer.is_valid():
        refresh_token = serializer.validated_data["refresh_token"]
        try:
            token_obj = RefreshToken.objects.get(
                token=refresh_token, is_valid=True, expires_at__gt=timezone.now()
            )
            token_obj.is_valid = False
            token_obj.save()

            access_token = generate_access_token(token_obj.user)
            new_refresh_token = generate_refresh_token(token_obj.user)

            return Response(
                {"access_token": access_token, "refresh_token": new_refresh_token}
            )
        except ObjectDoesNotExist:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=RefreshTokenSerializer,
    responses={200: "Success", 401: "Unauthorized", 400: "Bad Request"},
)
@api_view(["POST"])
def logout(request):
    """
    Invalidate refresh token.

    Parameters:
        - refresh_token (string): UUID refresh token (required)

    Returns:
        - success (string): Logout confirmation message

    Responses:
        - 200: Logout successful
        - 401: Invalid refresh token
        - 400: Bad request (validation errors)
    """
    serializer = RefreshTokenSerializer(data=request.data)
    if serializer.is_valid():
        try:
            token = RefreshToken.objects.get(
                token=serializer.validated_data["refresh_token"]
            )
            token.is_valid = False
            token.save()
            return Response({"success": "User logged out."})
        except ObjectDoesNotExist:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Retrieve the authenticated user's information.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        responses={200: UserSerializer},
        operation_description="Retrieve user information.",
    )
    def list(self, request):
        """Retrieve user information."""
        return Response(self.serializer_class(request.user).data)

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "Bad Request"},
        operation_description="Update user information.",
    )
    def update(self, request, *args, **kwargs):
        """Update user information."""
        return super().update(request, *args, **kwargs)


def generate_access_token(user):
    payload = {
        "user_id": user.id,
        "exp": timezone.now() + timedelta(seconds=settings.ACCESS_TOKEN_LIFETIME),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user):
    token = uuid.uuid4()
    RefreshToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(days=settings.REFRESH_TOKEN_LIFETIME),
    )
    return token
