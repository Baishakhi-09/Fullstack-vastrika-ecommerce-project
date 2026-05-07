from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [

    # ---------- Auth ---------- #
    path("signup/", views.signup, name="auth_signup"),
    path("login/", views.login_view, name="auth_login"),
    path("logout/", views.logout_view, name="auth_logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ---------- User ---------- #
    path("session/", views.session_status, name="session_status"),
    path("user/me/", views.user_me, name="user_me"),
    path("user/profile/", views.profile, name="user_profile"),
    path("user/profile/update/", views.update_profile, name="update_profile"),

    # ---------- OTP & password ---------- #
    path("otp/send/", views.send_forgot_password_otp, name="send_forgot_password_otp"),
    path("otp/resend/", views.resend_forgot_password_otp, name="resend_forgot_password_otp"),
    path("otp/verify/", views.verify_forgot_password_otp, name="verify_forgot_password_otp"),
    path("password/reset/", views.reset_password_with_otp, name="reset_password_with_otp"),

    # ---------- Newsletter ---------- #
    path("newsletter/subscribe/", views.subscribe_newsletter, name="newsletter_subscribe"),
]