from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views


app_name = "accounts"


urlpatterns = [

    # =====================================================
    # AUTH
    # =====================================================

    path(
        "auth/signup/",
        views.signup,
        name="signup",
    ),

    path(
        "auth/login/",
        views.login_view,
        name="login",
    ),

    path(
        "auth/logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "auth/session/",
        views.session_status,
        name="session_status",
    ),

    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # =====================================================
    # USER
    # =====================================================

    path(
        "user/me/",
        views.user_me,
        name="user_me",
    ),

    path(
        "user/profile/",
        views.profile,
        name="user_profile",
    ),

    # =====================================================
    # PASSWORD RESET & OTP
    # =====================================================

    path(
        "password/otp/send/",
        views.send_forgot_password_otp,
        name="send_forgot_password_otp",
    ),

    path(
        "password/otp/resend/",
        views.resend_forgot_password_otp,
        name="resend_forgot_password_otp",
    ),

    path(
        "password/otp/verify/",
        views.verify_forgot_password_otp,
        name="verify_forgot_password_otp",
    ),

    path(
        "password/reset/",
        views.reset_password_with_otp,
        name="reset_password_with_otp",
    ),

    # =====================================================
    # NEWSLETTER
    # =====================================================

    path(
        "newsletter/subscriptions/",
        views.subscribe_newsletter,
        name="newsletter_subscribe",
    ),
]