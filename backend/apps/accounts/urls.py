from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views


app_name = "accounts"


urlpatterns = [

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "signup/",
        views.signup,
        name="signup",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # =====================================================
    # SESSION
    # =====================================================

    path(
        "session/",
        views.session_status,
        name="session_status",
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
        name="profile",
    ),

    path(
        "user/profile/update/",
        views.update_profile,
        name="update_profile",
    ),

    # =====================================================
    # PASSWORD RESET & OTP
    # =====================================================

    path(
        "password/otp/send/",
        views.send_forgot_password_otp,
        name="send_password_otp",
    ),

    path(
        "password/otp/resend/",
        views.resend_forgot_password_otp,
        name="resend_password_otp",
    ),

    path(
        "password/otp/verify/",
        views.verify_forgot_password_otp,
        name="verify_password_otp",
    ),

    path(
        "password/reset/",
        views.reset_password_with_otp,
        name="reset_password",
    ),

    # =====================================================
    # NEWSLETTER
    # =====================================================

    path(
        "newsletter/subscribe/",
        views.subscribe_newsletter,
        name="newsletter_subscribe",
    ),
]