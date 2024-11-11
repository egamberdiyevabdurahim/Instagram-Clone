from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('app_user.urls')),
    path('api/post/', include('app_post.urls')),
]
