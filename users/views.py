import requests
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlencode
from rest_framework import status

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users import serializers

User = get_user_model()


class SignUpView(CreateAPIView):
    serializer_class = serializers.SignUpSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        signer = signing.TimestampSigner()  # 서명기능을 제공. sercet_key 를 가지고 특정한 값을 암호화
        signed_user_email = signer.sign(user.email)
        signer_dump = signing.dumps(signed_user_email)

        # http://127.0.0.1:8000/users/verify/?code={signer_dump}/
        self.verify_link = self.request.build_absolute_uri(f'/api/v1/users/verify/?code={signer_dump}')
        subject = '[Tabling] 회원가입 인증 메일입니다.'
        message = f'안녕하세요. {user.email}님, 회원가입을 완료하기 위해 아래 링크를 클릭해주세요.\n{self.verify_link}'

        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


class VerifyEmailView(APIView):
    def get(self, request):
        code = request.GET.get('code')  # 쿼리파라미터로 전달받은 코드

        signer = signing.TimestampSigner()
        try:
            decoded_user_email = signing.loads(code)  # signing.loads() 메서드로 쿼리파라미터로 전달받은 서명된 코드를 디코딩
            user_email = signer.unsign(decoded_user_email, max_age=60 * 5)  # 디코딩된 문자열을 서명해제하여 이메일을 가져옴
        except (TypeError, signing.SignatureExpired):  # 만약 타입 에러 또는 만료된 코드 에러가 뜨면 해당 내용을 에러로 반환
            return Response({"detail": "Invalid or expired verification code"}, status=status.HTTP_400_BAD_REQUEST)

        # 에러없이 성공적으로 서명해제하면 해당 이메일로 유저객체를 가져옴, 해당되는 유저가 없으면 404에러 반환
        user = get_object_or_404(User, email=user_email)
        user.is_active = True  # 해당 유저의 is_active 필드를 True로 변경하여 계정 활성화
        user.save()
        return Response({"detail": "Email verification successful"}, status=status.HTTP_200_OK)


class SessionLoginAPIView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            login(request, serializer.validated_data.get('user'))
            return Response({'message': 'login successful.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.session.flush()
        logout(request)
        return Response({'message': 'logout successful.'}, status=status.HTTP_200_OK)


class KakaoLoginView(APIView):
    def get(self, request):
        authorize_url = 'https://kauth.kakao.com/oauth/authorize'
        query_params = {
            'client_id': settings.KAKAO_CLIENT_ID,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'response_type': 'code',
            'prompt': 'login'
        }
        request_url = f"{authorize_url}?{urlencode(query_params)}"
        return redirect(request_url)


class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Code not provided'}, status=status.HTTP_400_BAD_REQUEST)

        token_url = "https://kauth.kakao.com/oauth/token"
        query_params = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "code": code,
        }

        token_response = requests.post(token_url, params=query_params)
        if token_response.status_code != 200:
            return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)

        token_data = token_response.json()
        access_token = token_data.get('access_token')

        profile_response = self.get_kakao_profile_response(access_token)
        if profile_response.status_code != 200:
            return Response({'error': 'Failed to obtain user profile'}, status=status.HTTP_400_BAD_REQUEST)

        profile_data = profile_response.json()
        kakao_account = profile_data.get('kakao_account')

        email = kakao_account.get('email')
        nickname = kakao_account.get('profile').get('nickname')

        refresh_token, access_token = self.login_process(email=email, nickname=nickname)

        return Response({
            'refresh_token': refresh_token,
            'access_token': access_token,
            'email': email,
            'nickname': nickname
        }, status=status.HTTP_200_OK)

    def get_kakao_profile_response(self, token):
        profile_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        profile_response = requests.get(profile_url, headers=headers)
        return profile_response

    def login_process(self, email, nickname):
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.is_active = True
            user.nickname = nickname
            user.set_unusable_password()
            user.save()

        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)

        return str(refresh_token), access_token

