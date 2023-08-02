from rest_framework import serializers

from customers.models import Customer
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = serializers.SerializerMethodField()
    code = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = (
            "id", "customer", "is_paid", "discount", "city", "body", "postal_code", "phone_number", "status", "coupon",
            "code", "transaction_code", "items",
        )

    def get_items(self, obj):
        items = obj.items.all()
        return OrderItemSerializer(instance=items, many=True).data

class CustomerUnpaidOrdersSerializer(serializers.ModelSerializer):
    unpaid_orders = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('unpaid_orders',)

    def get_unpaid_orders(self, obj):
        if obj:
            unpaid_orders = obj.orders.filter(is_paid=False)
            result = OrderSerializer(unpaid_orders, many=True).data
        else:
            result = {'unpaid_orders': None}
        return result
