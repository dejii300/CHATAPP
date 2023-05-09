from django.shortcuts import render, redirect,  get_object_or_404
from .models import *
from django.http import JsonResponse
import json
from .forms import *
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.



@login_required
def invites_recieved_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invatations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {'qs': results, 'is_empty': is_empty}

    return render(request, 'profiles/my_invites.html', context)

@login_required
def accept_invatation(request):
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
def reject_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(pk=pk)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:my-invites-view')


@login_required
def invite_profile_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {'qs': qs}

    return render(request, 'profiles/to_invite_list.html', context)

@login_required
def profile_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context = {'qs': qs}

    return render(request, 'profiles/profiles_list.html', context)


@login_required(login_url='login')
def friend_profile(request,pk):
    friend = Profile.objects.get(user_id=pk)
    user = request.user.profile
    profile = Profile.objects.get (id=friend.user.id)
    context = {'friend':friend, 'user':user, 'profile':profile}
    return render(request, 'profiles/frnd_p.html', context)
    
@login_required
def Index(request):
    user = request.user
    friends = user.friends.all()
    context ={'user':user, 'friends':friends}
    return render(request, 'profiles/index.html', context)

def friend_request(request):
    return render(request, 'profiles/frnd_request.html')

@login_required(login_url='login')
def settingPage(request):
    user = request.user.profile
    form = userForm(instance=user)
    
    if request.method == 'POST':
        form = userForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'profiles/settings.html', context)

@login_required
def Detail(request,pk):
    friend = Profile.objects.get(user_id=pk)
    user = request.user.profile
    profile = Profile.objects.get (id=friend.user.id)
    chats = ChatMessage.objects.all()
    reci_chats = ChatMessage.objects.filter( msg_sender=profile, msg_receiver=user )
    reci_chats.update(seen=True)
    form = ChatMessageForm()
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.msg_sender = user
            chat_message.msg_receiver = profile
            chat_message.save()
            return redirect("detail", pk=profile.id)

    context = {'friend':friend, 'form':form, 'user':user, 'profile':profile, 'chats':chats, 'num': reci_chats.count()}
    return render(request, 'profiles/detail.html', context)

@login_required
def sentMessages(request, pk):
    user = request.user.profile
    friend = Profile.objects.get(user_id=pk)
    profile = Profile.objects.get(id=friend.user.id)
    data = json.loads(request.body)
    new_chat = data["msg"]
    new_chat_message = ChatMessage.objects.create(body=new_chat, msg_sender=user, msg_receiver=profile, seen=False)
    print(new_chat)
    return JsonResponse(new_chat_message.body, safe=False)

@login_required
def receivedMessages(request, pk):
    user = request.user.profile
    friend = Profile.objects.get(user_id=pk)
    profile = Profile.objects.get(id=friend.user.id)
    arr = []
    chats = ChatMessage.objects.filter( msg_sender=profile, msg_receiver=user )
    for chat in chats:
        arr.append(chat.body)
    return JsonResponse(arr, safe=False)    

@login_required
def chatNotification(request):
    
   user = request.user.profile
   friends = user.friends.all()
   arr = []
   for friend in friends:
    chats = ChatMessage.objects.filter(msg_sender__id=friend.profile.id, msg_receiver=user, seen=False)
    arr.append(chats.count())

   return JsonResponse(arr, safe=False)


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profiles_list.html'
    # context_object_name = 'qs'
    
    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver =[]
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context
    
    
def send_invataion(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')


def remove_from_friends(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender)))
        
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')
