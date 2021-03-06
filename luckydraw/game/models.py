from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import time

class OTP(models.Model):
    """
    Model to store Otp of user And verify user.
    """
    receiver = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.IntegerField(null=False,blank=False)
    sent_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ("%s has received otps: %s" %(self.receiver.email,self.otp))


class Event(models.Model):
    """
    creates table for various gaming events.
    """
    name = models.CharField(max_length=256, null=False, blank=False)
    start_time = models.DateTimeField(null=False,blank=False)
    end_time = models.DateTimeField(null=True,blank=True)
    result_declared = models.BooleanField(default=False)

    def __str__(self):
        return ("%s" %(self.name))


class Ticket(models.Model):
    """
    Model to create ticket table.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100,null=False, blank=False,default="")
    created_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True, blank=False)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return ("%s ordered %s"%(self.user.username,self.code))


class Membership(models.Model):
    """
    Create a membership table to keep the track of 
    which user participated in which event and using which ticket.
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE, null=True) 
    participated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ("%s particapated in %s"%(self.user.username,self.event.name))

    class Meta:
        unique_together = [['user', 'ticket'],['event','user']]


class Rewards(models.Model):
    """
    Keeps the record of prizes in a event and quantity.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reward = models.CharField(max_length=200,null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return ("%s has %s %d")%(self.event.name,self.reward, self.quantity)


class Winner(models.Model):
    """
    To keep the record of winners of each event.
    """
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ticket = models.OneToOneField(Ticket,on_delete=models.CASCADE)
    reward = models.CharField(max_length=200,null=True,blank=True)

