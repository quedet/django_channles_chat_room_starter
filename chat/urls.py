from django.urls import path

from chat.views import index

urlpatterns = [
    path('', index, name='index')
]