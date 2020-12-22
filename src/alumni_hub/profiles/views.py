from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
@login_required
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form    = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    confirm = False
    
    if request.method=="POST":
        if form.is_valid():
            form.save()
            confirm = True

    context = {
        'profile': profile,
        'form'   : form,
        'confirm': confirm,
    }

    return render(request, 'profiles/my_profile.html', context)

@login_required
def invites_recieved_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitation_recieved(profile)
    results = list(map(lambda x: x.sender, qs))  #to display only sender name instead as showm in relationship ie testUser 23123- dhruv3123.
    is_empty = False
    
    if len(results)==0:
        is_empty = True

    context = {
        'qs'       : results,
        'is_empty' : is_empty,
    }

    return render(request, 'profiles/my_invites.html', context)

@login_required
def accept_invitations(request):
    if request.method=="POST":  
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:my-invites-view')

@login_required
def reject_invitations(request):
    if request.method=="POST":  
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:my-invites-view')

@login_required
def invite_profile_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {
        'qs' : qs,
    }  
    return render(request, 'profiles/to_invite_list.html', context)

@login_required
def profile_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context = {
        'qs' : qs,
    }  

    return render(request, 'profiles/profile_list.html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    def get_object(self):
        slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=slug)
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user    = User.objects.get(username__iexact=self.request.user) # remember 2 underscore
        profile = Profile.objects.get(user=user)
        #context['profile'] = profile
        rel_r   = Relationship.objects.filter(sender=profile) #by us to diff user
        rel_s   = Relationship.objects.filter(receiver=profile) #by diff user to our profile

        rel_receiver = []
        rel_sender = []

        for item in rel_r:
            rel_receiver.append(item.receiver.user)

        for item in rel_s:
            rel_sender.append(item.sender.user)
        context['rel_receiver'] = rel_receiver
        context['rel_sender'] = rel_s
        context['posts'] = self.get_object().get_all_author_post()
        context['len_post'] = True if len(self.get_object().get_all_author_post())>0 else False
         
        return context




class ProfileListView(LoginRequiredMixin, ListView):
    model               = Profile
    template_name       = 'profiles/profile_list.html'
    #context_object_name = 'qs' # we can use object_list instead 'qs'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user    = User.objects.get(username__iexact=self.request.user) # remember 2 underscore
        profile = Profile.objects.get(user=user)
        #context['profile'] = profile
        rel_r   = Relationship.objects.filter(sender=profile) #by us to diff user
        rel_s   = Relationship.objects.filter(receiver=profile) #by diff user to our profile

        rel_receiver = []
        rel_sender = []

        for item in rel_r:
            rel_receiver.append(item.receiver.user)

        for item in rel_s:
            rel_sender.append(item.sender.user)
        context['rel_receiver'] = rel_receiver
        context['rel_sender']   = rel_sender
        context['is_empty']     = False

        if self.get_queryset() == 0:
            context['is_empty'] = True
        
        return context

@login_required
def send_invitation(request):
    if request.method=='POST':
        pk       = request.POST.get('profile_pk')
        user     = request.user
        sender   = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
        
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

@login_required
def remove_from_friends(request):
    if request.method=='POST':
        pk       = request.POST.get('profile_pk')
        user     = request.user
        sender   = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
                (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
                )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')