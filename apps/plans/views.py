from django.shortcuts import render
from rest_framework import generics
from .models import Plan
from .serializers import PlanSerializer

# Create your views here.

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
