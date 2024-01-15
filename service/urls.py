# import path
from django.urls import path

# import views from service app
from . import views

urlpatterns = [
    # remove bg
    path("remove_bg/", views.remove_background_api, name="remove_bg"),
]
