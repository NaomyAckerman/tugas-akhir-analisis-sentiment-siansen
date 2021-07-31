from django.contrib import admin
from django.urls import path
from analisis_sentimen.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    # path('upload/', upload, name='upload'),
]
