from django.urls import path
from .views import TournamentListCreateView

urlpatterns = [
    path('tournaments/', TournamentListCreateView.as_view(), name='tournament-list-create'),
]
