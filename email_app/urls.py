from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('compose/', views.compose_mail, name='compose'),
    path('history/', views.email_history, name='history'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('contacts/delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('profile/', views.profile_view, name='profile'),
]