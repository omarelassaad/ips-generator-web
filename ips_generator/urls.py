from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from ips import views as ips_views
from django.shortcuts import redirect

def redirect_to_ips(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_ips, name='root'),  # Add root URL
    path('admin/', admin.site.urls),
    path('ips/', include('ips.urls')),  # Include URLs from the ips app
    path('accounts/login/', ips_views.login_view, name='login'),
    path('accounts/logout/', ips_views.logout_view, name='logout'),
    path('accounts/register/', ips_views.register_view, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add this for production static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
