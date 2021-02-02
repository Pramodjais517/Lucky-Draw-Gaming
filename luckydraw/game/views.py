
# Create your views here.
from rest_framework.views import APIView
from .serializers import *
from .permissions import *
from rest_framework import permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login,logout
from .models import OTP
from random import *
from django.template.loader import render_to_string
from rest_framework import permissions, status
from django.core.mail import send_mail
from luckydraw.settings import EMAIL_HOST_USER
from threading import Thread


def send_otp(user):
    otp = OTP.objects.filter(receiver=user)
    if otp:
        otp.delete()
    code = randint(100000, 1000000)
    otp = OTP.objects.create(
            otp=code, 
            receiver=user
        )
    otp.save()
    subject = 'Verify your account'
    message = render_to_string('account_activation.html', {
            'user': user,
            'OTP': code,
        })
    from_mail = EMAIL_HOST_USER
    to_mail = [user.email]
    send_mail(subject, message, from_mail, to_mail, fail_silently=False)


class SignUp(APIView):
    """
    View for signing up user with email verification.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """
        Accepts Email and Password from the user 
        and generates a user object and sends OTP
        to the mail for account verification.
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  #validating the data received.
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=password
            )
        except(TypeError, ValueError, OverflowError):
            user = None
        if user:
            user.is_active = False
            user.save()  #User is created   
            msg_thread = Thread(target=send_otp,args=(user,)) # Setting a thread for sending email.
            msg_thread.start()
            return Response({'user_id': user.id },status=status.HTTP_201_CREATED)
        return Response({'error':'Invalid request'},status=status.HTTP_501_NOT_IMPLEMENTED)


class Activate(APIView):
    """
    View to verify the stored otp and the otp entered by user.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, user_id,*args,**kwargs):
        serializer = OTPSerializer(data=request.data,context={'user_id':user_id})
        serializer.is_valid(raise_exception=True)  # validating the data received.
        code_otp = serializer.validated_data['otp']
        otp = OTP.objects.get(receiver=user_id)
        receiver = User.objects.get(id=user_id)
        if str(otp.otp) == str(code_otp):
            if not receiver.is_active:
                serializer.is_valid(raise_exception=True)
                receiver.is_active = True
                receiver.save()
            otp.delete()
            refresh, access = get_tokens_for_user(receiver)
            return Response({'message': 'Successful', 'refresh': refresh, 'access': access})
        else:
            raise ValidationError({'error': 'Invalid OTP'})


class ResendOtp(APIView):
    """
    views for resend the otp.
    """
    serializer_class = OTPSerializer
    permission_classes = (permissions.AllowAny,IsNotActive)

    def get(self,request,user_id,*args,**kwargs):
        try:
            user = User.objects.get(id=user_id,is_active=False)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is None:
            return Response({'error':'Not a valid user!'})
        msg_thread = Thread(target=send_otp,args=(user,))
        msg_thread.start()
        return Response({'user_id': user_id }, status=status.HTTP_201_CREATED)