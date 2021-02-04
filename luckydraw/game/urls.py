from django.conf.urls import url
from .views import *
from django.conf import settings
from django.urls import include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from luckydraw.settings.base import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL


router = DefaultRouter()
router.register(r'event', EventView)  #api for performing CRUD on Event, buying tickets,and computing winner


urlpatterns = [ 
    url(r'', include(router.urls)), 
    url(r'^signup/$', SignUp.as_view()),  # api  for sign up
    url(r'^activate/(?P<user_id>[0-9]+)/$', Activate.as_view()), # to verify the OTP sent on mail  ex - /activate/{user_id}/
    url(r'^resendotp/(?P<user_id>[0-9]+)/$', ResendOtp.as_view()), # to resend OTP if OTP expires or not sent ex- /resendotp/{user_id}/
    url(r'^login/$', LoginView.as_view()),    # to login 
    url(r'^winner-list/$', WinnerListView.as_view()), # to get the list of winners from past 1 week events.
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += static(STATIC_URL,document_root=STATIC_ROOT)