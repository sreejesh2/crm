from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .models import User

class JWTBlacklistAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            raw_token = self.get_raw_token(self.get_header(request))
            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)
            self.blacklist_checker(validated_token)
            request.user = self.get_user(validated_token)

        except TokenError as e:
            return self.handle_token_error(str(e))

    def get_header(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()
        auth_header_prefix = 'Bearer'

        if not auth or auth[0].lower() != auth_header_prefix.lower():
            return None

        if len(auth) == 1:
            return None
        elif len(auth) > 2:
            return None

        return auth[1]

    def get_raw_token(self, header):
        return header

    def get_validated_token(self, raw_token):
        try:
            return AccessToken(raw_token)
        except TokenError:
            raise TokenError('Invalid token')

    def blacklist_checker(self, validated_token):
        user_id = validated_token.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise TokenError('User does not exist')

        if user.current_token and user.current_token != str(validated_token):
            raise TokenError('Token is blacklisted')

    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None  # Return None or handle as appropriate for your application

        return user

    def handle_token_error(self, error_message):
        return JsonResponse({'error': error_message}, status=401)
