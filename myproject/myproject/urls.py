from django.contrib import admin
from django.urls import path
from app import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('register/', views.register),
    path('profile/', views.profile),
    path("user/", views.UserListView.as_view()),
    path('logout/', views.logout),
]
