from django.urls import path
from .views import PlanListView

urlpatterns = [
    path('api/v1/plans/', PlanListView.as_view(), name='plan-list'),
] 