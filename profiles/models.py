from django.db import models
from .utils import get_random_code
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.urls import reverse

# Create your models here.

class ProfileManager(models.Manager):

    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender) 
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
        print(qs)

        accepted = set([])
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
        print(accepted)

        available = [profile for profile in profiles if profile not in accepted]
        print(available)
        return available         

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles 


class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    pic = models.ImageField(default="profile1.png", upload_to="images", blank=True, null=True)
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    objects = ProfileManager()

    @property
    def picURL(self):
        try:
            url = self.pic.url
        except:
            url = ''
        return url 

    def __str__(self):
        return f"{self.user.username}"
    
    def get_absolute_url(self):
        return reverse("profiles:detail", kwargs={"pk": self.pk})

    def get_friends(self):
        return self.friends.all()
    
    def get_friends_no(self):
        return self.friends.all().count()
    
    def get_posts_no(self):
        return self.posts.all().count()
    
    def get_all_authors_posts(self):
        return self.posts.all()
    
    def get_likes_given_no(self):
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value=='Like':
                total_liked += 1
        return total_liked

    def get_likes_received_no(self):
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            total_liked += item.liked.all().count()
        return total_liked            

    

STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)                  

class RelationshipManager(models.Manager):
    def invatations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
     
    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"     

class ChatMessage(models.Model):
    body = models.TextField()
    msg_sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="msg_sender")
    msg_receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="msg_receiver")  
    seen = models.BooleanField(default=False)    

    def __str__(self):
        return self.body      