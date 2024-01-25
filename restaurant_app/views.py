# views.py
from rest_framework import viewsets,status
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .serializer import (
    RestaurantSerializer,
    MenuSerializer,
    MenuItemSerializer,
    OrderSerializer,
    PaymentSerializer
)
import stripe

from stripesetting.models import StripePayment
from rest_framework.response import Response

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        user = request.user

        if user.role == "OWNER":
            request.data['owner'] = user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response("You are not allowed", status=status.HTTP_403_FORBIDDEN)


    def update(self, request, *args, **kwargs):
        user = request.user
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if  user.role == "OWNER":
            request.data['owner'] = user.id

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("You are not allowed to update this restaurant.", status=status.HTTP_403_FORBIDDEN)
        
    def get_queryset(self):
        user = self.request.user
        if user.role == "OWNER":
            return Restaurant.objects.filter(owner=user)
        else:
            return Restaurant.objects.all()

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role == "OWNER":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response("You are not allowed to create a menu for this restaurant.", status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        user = request.user
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if user.role == "OWNER":
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("You are not allowed to update this menu.", status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        user = self.request.user
        if user.role == "OWNER":
            return Menu.objects.filter(restaurant__owner=user)
        else:
            return Menu.objects.all()

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role == "OWNER":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response("You are not allowed to create an item for this menu.", status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        user = request.user
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if user.role == "OWNER":
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("You are not allowed to update this item.", status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        user = self.request.user
        if user.role == "OWNER":
            return MenuItem.objects.filter(menu__restaurant__owner=user)
        else:
            return MenuItem.objects.all()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(methods=["GET"], detail=False, url_path="payable")
    def get_payable(self, request):
        user = request.user
        payable_orders = Order.objects.filter(user=user, is_paid=False)
        serialized_orders = OrderSerializer(payable_orders, many=True).data
        return Response(serialized_orders)
    
    @action(methods=["POST"], detail=False, url_path="pay_stripe")
    def pay_stripe(self, request, *args, **kwargs):
        try:
            api_key = StripePayment.objects.first().api_key

            total_amount = request.data.get("amount")  #it will comes from payable in frontend
            stripe.api_key = api_key
            success_url = f'http://127.0.0.1:8000/?total_payable={total_amount}'
            cancel_url = 'http://127.0.0.1:8000/api/restaurant/payments/payable/'

            line_items_data = [
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(float(total_amount) * 100),
                        "product_data": {
                            "name": "Your Bill",
                        },
                    },
                    "quantity": 1,
                }]
            session_data = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items_data,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )

            if session_data:
                order_id = request.data.get("order_id")
                payment = Payment.objects.create(order_id=order_id, payment_status=True)
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()
                return Response(
                    {
                        "checkout_url": session_data.url,
                        "session_data": session_data,
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)