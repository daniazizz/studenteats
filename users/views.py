from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! YOu are now able to login!')
            return redirect('login')
    else:        
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required # Decorator to add functionality
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user) ## Instance argument make it so that the fields are filled with the current data
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)## Files argument is for the image
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user) ## Arguments make it so that the fields are filled with the current data
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


