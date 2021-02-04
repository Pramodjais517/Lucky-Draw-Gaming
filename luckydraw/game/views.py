
# Create your views here.
from rest_framework.views import APIView
from .serializers import *
from .permissions import *
from rest_framework import permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login,logout
from .models import OTP, User
from random import randint
from django.template.loader import render_to_string
from rest_framework import permissions, status
from django.core.mail import send_mail
from luckydraw.settings.base import EMAIL_HOST_USER
from threading import Thread
from .token import get_tokens_for_user
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import action
from django.http import JsonResponse
import datetime




def send_otp(user):
    """
    Accepts the user and generates a OTP for that user and sends it to mail.
    """
    otp = OTP.objects.filter(receiver=user)
    if otp:
        otp.delete()
    #generating six digit random number for OTP
    code = randint(100000, 1000000)
    otp = OTP.objects.create(otp=code, receiver=user)
    otp.save()
    # sending mail witht the message as body.
    subject = 'Verify your account'
    message = render_to_string('account_activation.html', {
                                'user': user,
                                'OTP': code,})
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
            user = User.objects.create_user(username=email, 
                                            email=email, password=password)
        except(TypeError, ValueError, OverflowError):
            user = None
        if user:
            user.is_active = False
            user.save()  #User is created   
            # Setting a thread for sending email.
            msg_thread = Thread(target=send_otp,args=(user,))
            msg_thread.start()
            return Response({'user_id': user.id }, status=status.HTTP_201_CREATED)
        return Response({'error':'Invalid request'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class Activate(APIView):
    """
    View to verify the stored otp and the otp entered by user.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, user_id,*args,**kwargs):
        """
        Accepts the OTP and verifies the user.
        """
        serializer = OTPSerializer(data=request.data, context={'user_id':user_id})
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
            return Response({'refresh': refresh, 'access': access})
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
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None
        if user is None:
            return Response({'error':'Not a valid user!'})
        msg_thread = Thread(target=send_otp,args=(user,))
        msg_thread.start()
        return Response({'user_id': user_id }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Used for logging in.
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """"
        accepts email and password and generates
        token to maintain session via token.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(username=email)
        refresh, access = get_tokens_for_user(user)
        return Response({'refresh': refresh, 'access': access}, status=status.HTTP_200_OK)


class EventView(viewsets.ModelViewSet):
    """
    View for performing CRUD of Event and buying ticket for event.  
    """
    serializer_class = EventSerializer
    serializer_action_classes = {'buy_ticket': TicketSerializer,}
    permission_classes_by_action = {'create': [IsAdmin,],
                                    'buy_ticket':[permissions.IsAuthenticated],
                                    'compute_winner':[IsAdmin]}
    permission_classes = (permissions.AllowAny,)
    queryset = Event.objects.raw('select * from game_event where start_time > current_timestamp')

    def create(self, request, *args, **kwargs):
        """
        accepts the details from admin and creates the event object.
        """
        return super(EventView, self).create(request, *args, **kwargs)

    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except (KeyError, AttributeError): 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        try:
            # return serializer_classes depending on `action`
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            # returns the default serializer class
            return super().get_serializer_class()

    @action(detail=True, methods=['get'], name='Buy Ticket')
    def buy_ticket(self, request,pk=None,*arg,**kwargs):
        """
        accepts the event_id and perform order placement for that event.
        """
        # checking if event requested exists or not
        try:
            event = Event.objects.get(id=pk)
        except(KeyError, AttributeError, OverflowError, ObjectDoesNotExist):
            event = None
        if not event:
            return Response({'error':'No such event exists'},status=status.HTTP_403_FORBIDDEN)
        #checking if user is buying ticket again in the same event.
        user=User.objects.get(username=request.user.username)
        try:
            membership = Membership.objects.get(event=event,user=user)
        except(KeyError, AttributeError, OverflowError, ObjectDoesNotExist):
            membership = None
        if membership:
            return Response({"info":"You have already participated in the contest"},status=status.HTTP_403_FORBIDDEN)  
        # if user has not already participated in the game
        # let him buy ticket and participate
        # generating ticket for user
        ticket = Ticket.objects.create(user=user)  
        ticket.code = event.name.upper() + str(ticket.id + 1000)
        ticket.expires_on = event.end_time
        ticket.save()
        # Adding membership of that user into the contest i.e event 
        try:
            membership = Membership.objects.create(user=user,event=event,ticket=ticket)
            membership.save()
        except(KeyError, AttributeError, OverflowError):
            membership=None
        if membership: 
            return Response({'info':'Order completed','Ticked code':ticket.code},status=status.HTTP_200_OK)
        return Response({'error':'Try again'},status=status.HTTP_501_NOT_IMPLEMENTED)


    @action(detail=True, methods=['get'], name='Buy Ticket')
    def compute_winner(self, request,pk=None,*arg,**kwargs):
        """
        Accepts event id and computes the winner of the event.
        This can be only done by Admin.
        """
        # checking if event requested exists or not
        try:
            event = Event.objects.get(id=pk)
        except(KeyError, AttributeError, OverflowError, ObjectDoesNotExist):
            event = None
        if not event:
            return Response({'error':'No such event exists'},status=status.HTTP_403_FORBIDDEN)
        # If result is already declared
        if event.result_declared:
            return Response({'info':'Result already declared'},status=status.HTTP_200_OK)
        # Make a list of all the participants in the event
        member_list = list(Membership.objects.filter(event=event).values())  
        # make the list of all the ticket ids
        ticket_list = [i['ticket_id'] for i in member_list]
        # map each ticket_id with the correspoinding user_id
        user_ticket_dict = {i['ticket_id']:i['user_id'] for i in member_list}
        total_tickets = len(ticket_list)
        # generate a random number between 0 to len(participants)
        winner_index = randint(0,total_tickets-1)
        # ticket id corressponding to that random index will be winner
        winner_ticket = ticket_list[winner_index]
        winner_ticket = Ticket.objects.get(id=winner_ticket)
        winner_id = user_ticket_dict[winner_ticket.id]
        winner = User.objects.get(id=winner_id)
        #updating winner in event table.
        event.winner = winner
        event.result_declared=True
        event.save()
        return Response({'First_name': winner.first_name,'last_name':winner.last_name,
                        'ticket_code':winner_ticket.code}, status=status.HTTP_200_OK) 


class WinnerListView(APIView):
    """
    view for getting winner list of events in past 7 days i.e last one week.
    """
    serializer_class = EventSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self,request,*args,**kwargs):
        """
        Returns winner list containing event id (id) and Winner details
        """
        time_stamp = datetime.datetime.now() - datetime.timedelta(hours=7)
        data = Event.objects.filter(result_declared=True, start_time__range=[time_stamp,datetime.datetime.now()])
        serializer = WinnerListSerializer(data=data,many=True)
        serializer.is_valid()
        return Response({'winner-list':serializer.data},status=status.HTTP_200_OK)



          
        