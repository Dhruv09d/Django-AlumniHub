from django.db import models
from django.contrib.auth.models import User
from .utils import get_random_code
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.shortcuts import reverse 
# Create your models here.

class ProfileManager(models.Manager):
    
    def get_all_profiles_to_invite(self, sender):
        profiles  = Profile.objects.all().exclude(user=sender)
        profile  = Profile.objects.get(user=sender)
        qs       = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
        #print(qs)
        accepted = set([])

        for rel in qs:
            if rel.status=='accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
        #print(accepted)
        available = [profile for profile in profiles if profile not in accepted]
        #print(available)
        return available


    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles


class Profile(models.Model):
    first_name = models.CharField(max_length=120, blank=True) # blank=True make the field optional
    last_name  = models.CharField(max_length=120, blank=True)
    user       = models.OneToOneField(User, on_delete=models.CASCADE) # on_delete will delete profile if user delete it 
    college    = models.CharField(max_length=200)
    status     = models.CharField(default="Student",max_length=120, blank=True)
    bio        = models.TextField(default="NO bio...", max_length=300)
    email      = models.EmailField(max_length=200, blank=True)
    country    = models.CharField(max_length=120, blank=True)
    avatar     = models.ImageField(default='avatar.png', upload_to='') # install pillow
    friends    = models.ManyToManyField(User, blank=True, related_name='friends')
    slug       = models.SlugField(unique=True, blank=True)
    updated    = models.DateTimeField(auto_now=True)
    created    = models.DateTimeField(auto_now_add=True)

    objects    = ProfileManager() 
    def __str__(self):
        return f"{self.user.username}={self.created.strftime('%d-%m-%Y')}"
    
    def get_absolute_url(self):
        return reverse("profiles:profile-detail-view", kwargs={"slug": self.slug})

    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self):
        return self.friends.all().count()

    def get_posts_no(self):  # taking this from posts.models
        return self.posts.all().count()

    def get_all_author_post(self): # taking this from posts.models
        return self.posts.all()

    def get_likes_given(self): # taking this from posts.models
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value=='Like':
                total_liked += 1
        return total_liked

    def get_likes_recieved_no(self): # taking this from posts.models i have given a  related name= posts in posts.models.Posts 
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            total_liked += item.liked.all().count() # cannot use relative_name as there is no reversed realtionship in db
        return total_liked



    # next 6 line of code taken from StackOverflow to make the changing(change when press "save and continue" 
    # and revert when press again) slug acceptable 
    __initial_first_name = None
    __initial_last_name = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_first_name = self.first_name
        self.__initial_last_name = self.last_name

    def save(self, *args, **kwargs):
        ex = False
        to_slug = self.slug
        # need to modify this contidition 
        if self.first_name != self.__initial_first_name or self.last_name != self.__initial_last_name or self.slug=="": # to maintain code from stackoverflow
            if self.first_name and self.last_name:
                to_slug = slugify(str(self.first_name)+" "+str(self.last_name))
                ex = Profile.objects.filter(slug=to_slug).exists()
                while ex:
                    to_slug = slugify(to_slug +" "+ str(get_random_code()))
                    ex = Profile.objects.filter(slug=to_slug).exists()
            else:
                to_slug = str(self.user)
        
        self.slug = to_slug
        super().save(*args, **kwargs)


STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)

class RelationshipManager(models.Manager):
    def invitation_recieved(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs


class Relationship(models.Model):
    sender   = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status   = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated  = models.DateTimeField(auto_now=True)
    created  = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
