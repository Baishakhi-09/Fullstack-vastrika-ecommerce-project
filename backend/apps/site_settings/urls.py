from django.urls import path

from .views import (
    SettingTreeAPIView,
    SettingListAPIView,
    SettingUpdateAPIView,
    SettingFileUploadAPIView,
)

app_name = "site_settings"

urlpatterns = [
    path("tree/", SettingTreeAPIView.as_view(), name="tree"),
    path("", SettingListAPIView.as_view(), name="list"),
    path("update/", SettingUpdateAPIView.as_view(), name="update"),
    path("upload-file/", SettingFileUploadAPIView.as_view(), name="upload_file"),
]