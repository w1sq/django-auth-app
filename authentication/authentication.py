import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user_model().objects.get(id=payload["user_id"])
            return (user, None)
        except jwt.ExpiredSignatureError as exc:
            raise exceptions.AuthenticationFailed("Access token expired") from exc
        except (jwt.InvalidTokenError, IndexError) as exc:
            raise exceptions.AuthenticationFailed("Invalid token") from exc
        except get_user_model().DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("User not found") from exc
