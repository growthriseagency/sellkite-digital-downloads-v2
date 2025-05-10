from django.urls import path
from .views import StoreSubscriptionView, StoreRetrieveView, StoreOnboardingView

urlpatterns = [
    path('api/v1/stores/me/subscription/', StoreSubscriptionView.as_view(), name='store-subscription'),
    path('api/v1/stores/me/', StoreRetrieveView.as_view(), name='store-retrieve'),
    path('api/v1/stores/connect/', StoreOnboardingView.as_view(), name='store-onboarding'),
] 