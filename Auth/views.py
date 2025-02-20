from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib.auth import logout

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            print("form is valid")
            user = form.save()
            return render(request,'Auth/login.html',{'form' : form})
            # login(request, user)  # Log the user in after registration
            # return redirect('home')
        else:
            return render(request, 'Auth/register.html', {'form': form, "alert" : form.errors})
    
    return render(request, 'Auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomLoginForm()
    
    return render(request, 'Auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

# Create your views here.

def index(request):
    return render(request,'Auth/layout.html')