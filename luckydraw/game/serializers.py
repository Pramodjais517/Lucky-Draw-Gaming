from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator
from .models import *
from rest_framework import permissions, status
from django.utils import timezone
from datetime import timedelta



class UserSerializer(serializers.ModelSerializer):
    """
    serializer for creating user object
    """
    email = serializers.EmailField(required=True, 
                                allow_blank=False, 
                                allow_null=False,
                                validators=[UniqueValidator(queryset=User.objects.all(),
                                                               message="email already exists!",
                                                               lookup='exact')]
                            )
    password = serializers.CharField(
                            style={'input_type': 'password'}, 
                            required=True,
                            allow_blank=False, 
                            allow_null=False
                        )
    confirm_password = serializers.CharField(
                                    style={'input_type':'password'},
                                    required=True
                                    )

    class Meta:
        model = User
        fields = ('email','password','confirm_password')

    def validate(self, data):

        """
        function for emai and password validation.
        """
        password = data.get('password')
        pass_cnf = data.get('confirm_password')

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
        except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
            otp = None
        try:
            receiver = User.objects.get(id=user_id, is_active=False)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            receiver = None
        # If no such user or OTP exists.
        if otp is None or receiver is None:
            raise ValidationError({'error': 'Not a valid user'})
        #if OTP is expired.
        elif timezone.now() - otp.sent_at >= timedelta(days=0, hours=0, minutes=5, seconds=0):
            raise ValidationError({'error': 'OTP expired!'})
        #returning the validated data.
        return data

