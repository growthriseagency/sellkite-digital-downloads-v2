from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Store
from .serializers import StoreSubscriptionSerializer, StoreRetrieveSerializer
from apps.plans.models import Plan
from rest_framework.permissions import AllowAny

# Create your views here.

class StoreSubscriptionView(APIView):
    def get(self, request):
        # For now, just get the first store (simulate 'me')
        store = Store.objects.first()
        if not store:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StoreSubscriptionSerializer(store)
        return Response(serializer.data)

    def post(self, request):
        # Simulate plan change (expects 'plan_id' in request.data)
        store = Store.objects.first()
        if not store:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'detail': 'plan_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)
        store.current_plan = plan
        store.subscription_status = 'active'
        store.save()
        serializer = StoreSubscriptionSerializer(store)
        return Response(serializer.data)

    def delete(self, request):
        # Simulate cancel subscription
        store = Store.objects.first()
        if not store:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        store.subscription_status = 'canceled'
        store.save()
        serializer = StoreSubscriptionSerializer(store)
        return Response(serializer.data)

class StoreRetrieveView(APIView):
    def get(self, request):
        store = Store.objects.first()
        if not store:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StoreRetrieveSerializer(store)
        return Response(serializer.data)

class StoreOnboardingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        shopify_domain = request.data.get('shopify_domain')
        shopify_access_token = request.data.get('shopify_access_token')
        email = request.data.get('email')
        if not shopify_domain or not shopify_access_token:
            return Response({'detail': 'shopify_domain and shopify_access_token are required.'}, status=status.HTTP_400_BAD_REQUEST)
        default_plan = Plan.objects.filter(is_active=True).order_by('id').first()
        store, created = Store.objects.get_or_create(
            shopify_domain=shopify_domain,
            defaults={
                'shopify_access_token': shopify_access_token,
                'email': email,
                'is_active': True,
                'current_plan': default_plan,
            }
        )
        if not created:
            # Update access token and email if store already exists
            store.shopify_access_token = shopify_access_token
            if email:
                store.email = email
            store.is_active = True
            store.save()
        serializer = StoreRetrieveSerializer(store)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
