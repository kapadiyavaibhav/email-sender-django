from django.contrib import admin
from django.urls import path,include
from email_app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('email_app.urls')),
    
]
