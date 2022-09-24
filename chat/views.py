from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    users = User.objects.order_by("username")
    return render(request, 'index.html', {"users": users})