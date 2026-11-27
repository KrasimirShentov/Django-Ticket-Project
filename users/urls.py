"""
URL mappings for the User API
"""
from django.urls import path
from users import views


app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.CreateTokenView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('me/', views.ManageUserView.as_view(), name='me')
]
