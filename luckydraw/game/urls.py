from django.conf.urls import url
from .views import *
from django.conf import settings
from django.urls import include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'event', EventView)



urlpatterns = [ 
    url(r'', include(router.urls)),
    url(r'^signup/$', SignUp.as_view()),
    url(r'^activate/(?P<user_id>[0-9]+)/$', Activate.as_view()),
    url(r'^resendotp/(?P<user_id>[0-9]+)/$', ResendOtp.as_view()),
    url(r'^login/$', LoginView.as_view()),
    url(r'^winner-list/$', WinnerListView.as_view()),
]