from django.conf.urls import url
from .views import *
from django.conf import settings
from django.urls import include
from django.conf.urls.static import static

# from rest_framework import routers
# router = routers.SimpleRouter()
# router.register(r'users', UserViewSet)


urlpatterns = [ 
    url(r'^api/signup/$', SignUp.as_view()),
    url(r'^api/activate/(?P<user_id>[0-9]+)/$', Activate.as_view()),
    url(r'^api/resendotp/(?P<user_id>[0-9]+)/$', ResendOtp.as_view()),
    url(r'^api/login/$', LoginView.as_view()),
]