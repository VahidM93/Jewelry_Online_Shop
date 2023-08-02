from rest_framework import serializers
from .models import Order, OrderItem, Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
