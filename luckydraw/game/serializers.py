from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator
from .models import *
from rest_framework import permissions, status
from django.utils import timezone
from datetime import timedelta
import re
from django.core.exceptions import ObjectDoesNotExist




class UserSerializer(serializers.ModelSerializer):
    """
    serializer for creating user object
    """
    email = serializers.EmailField(required=True, allow_blank=False, 
                                   allow_null=False,validators=[UniqueValidator(queryset=User.objects.all(),
                                                        message="email already exists!",
                                                        lookup='exact')])
    password = serializers.CharField(style={'input_type': 'password'}, required=True,
                                    allow_blank=False, allow_null=False)
    confirm_password = serializers.CharField(style={'input_type':'password'},required=True)

    class Meta:
        model = User
        fields = ('first_name','last_name','email','password','confirm_password')

    def validate(self, data):

        """
        function for emai and password validation.
        """
        password = data.get('password')
        pass_cnf = data.get('confirm_password')
        email = data.get('email')
        regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.search(regex,email):
            raise ValidationError({"error": "Invalid email"})
        if password != pass_cnf:
               raise ValidationError("Password didn't matched ")
        if len(password) < 6:
               raise ValidationError("password of minimum 6 digit is required")
        else:
            return data


class OTPSerializer(serializers.ModelSerializer):
    """
    serializer for otp
    """

    class Meta:
        model = OTP
        fields = ['otp']


    def validate(self, data,*args,**kwargs):
        otp = data.get('otp')
        # if length is less than or greater than 4.
        user_id = self.context['user_id']
        if len(str(otp)) != 6:
            raise ValidationError({"error":"Invalid OTP"})
        try:
            otp = OTP.objects.get(receiver=user_id)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            otp = None
        try:
            receiver = User.objects.get(id=user_id, is_active=False)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            receiver = None
        # If no such user or OTP exists.
        if otp is None or receiver is None:
            raise ValidationError({'error': 'Not a valid user'})
        #if OTP is expired.
        elif timezone.now() - otp.sent_at >= timedelta(days=0, hours=0, minutes=5, seconds=0):
            raise ValidationError({'error': 'OTP expired!'})
        #returning the validated data.
        return data


class LoginSerializer(serializers.ModelSerializer):
    """serializer for Login using otp"""

    password = serializers.CharField(style={'input_type': 'password'},required=True,
                                     allow_blank=False,allow_null=False)

    class Meta:
        model = User
        fields = ['email','password']


    def validate(self,data):
        email = data.get('email')
        password = data.get('password')
        # regex for email validation.
        regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.search(regex,email):
            raise ValidationError({"error": "Invalid email"})
        try:
            user = User.objects.get(username=email)
            if user.check_password(password):
                pass
            else:
                user=None
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None
        if not user:
            raise ValidationError({'error': "Email or password incorrect"})
        return data


class EventSerializer(serializers.ModelSerializer):
    """
    Serialzer for CRUD of Event i.e lucky draw game.
    """

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('winner','result_declared')


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket buying and getting details
    """

    class Meta:
        model = Ticket
        fields ='__all__'
        read_only_fields = ('user','code','expires_on','is_used','created_on')


class UserListSerializer(serializers.ModelSerializer):
    """
    For embedding the serialized data into the WinnerlistSerializer
    for getting detailed data of the user.
    """

    class Meta:
        model = User
        fields = ['id','username','email']



class WinnerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing winner of last one weeks along with event id.
    """
    winner = UserListSerializer()

    class Meta:
        model = Event
        fields = ('id','winner')