from django.urls import path
from . import views

urlpatterns = [
    path('add-candidate/', views.AddCandidateView.as_view(), name='add_candidate'),
    path('vote-candidate/', views.VoteCandidateView.as_view(), name='vote_candidate'),
    path('display-votes/', views.DisplayVotesView.as_view(), name='display_votes'),
    path('verify-email/', views.SendEmailView.as_view(), name='send_otp'),
    path('verify-email/verify-otp/', views.VerifyEmailView.as_view(), name='verify_otp'),
    path('add-voters/', views.AddVoterView.as_view(), name='add-voters'),
]