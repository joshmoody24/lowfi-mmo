from django.urls import path, include
from accounts import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("password/change/", auth_views.PasswordChangeView.as_view(), name='password_change'),
    path("password/reset/", auth_views.PasswordResetView.as_view(), name='password_reset'),
]
