from django.contrib import admin
from django.views.generic.base import RedirectView
from django.urls import include, path

urlpatterns = [
    path('', RedirectView.as_view(url='polls/')),
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
