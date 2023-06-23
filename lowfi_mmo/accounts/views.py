from django.shortcuts import render, redirect
from django.contrib.auth.views import LogoutView
from django.shortcuts import reverse
from django.contrib.auth.models import User

def profile(request):
    return render(request, "profile.html", {"title": "Profile"})

def profile_edit(request):
    if(request.method == "POST"):
        request.user.username = request.POST.get("username")
        request.user.first_name = request.POST.get("first-name")
        request.user.last_name = request.POST.get("last-name")
        request.user.save()
        return redirect("profile")
        
    return render(request, "profile.html", {"edit_mode": True, "title": "Edit Profile"})