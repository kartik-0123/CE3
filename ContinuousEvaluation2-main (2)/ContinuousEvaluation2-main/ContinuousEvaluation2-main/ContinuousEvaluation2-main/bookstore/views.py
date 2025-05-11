from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages



def index(request):
    return render(request, 'bookstore/index.html')

# def index(request):
#     return render(request, 'index.html', {'username': request.user.username})

# def cards(request):
#     return render(request, 'bookstore/cards.html')
def cards(request):
    return render(request, 'bookstore/cards.html') 

def cart1(request):
    return render(request, 'bookstore/cart1.html')

def display(request):
    return render(request, 'bookstore/display.html')

def feedback(request):
    return render(request, 'bookstore/feedback.html')

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('bookstore_index')
#         else:
#             messages.error(request, 'Invalid credentials')
#     return render(request, 'bookstore/login.html')

# def logout_view(request):
#     logout(request)
#     return redirect('bookstore_index')

# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created for {username}!')
#             return redirect('bookstore_login')
#     else:
#         form = UserCreationForm()
#     return render(request, 'bookstore/register.html', {'form': form})