from django.contrib import admin
from django.urls import path , include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Include the i18n URLs

    path('api/',include('users.urls',namespace="users")),
    path('api/',include('store.urls',namespace="store")),
    path('api/',include('order.urls',namespace="order")),
    path('api/',include('basket.urls',namespace="basket")),
    path('api/',include('dashboard.urls',namespace="dashboard")),
    
    
    path('api-token-auth/',obtain_auth_token),
    path('api/token/',TokenObtainPairView.as_view()),
    
]
handler404 = 'utils.erorr_view.handler404'

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



