from decimal import Decimal
from django.conf import settings
from products.models import Product

CART_SESSION_ID = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
            cart[str(product.id)]['image'] = product.image

        for item in cart.values():
            item['total_price'] = Decimal(item['price']) * item['quantity']
            item['discount_price'] = Decimal(item['price_no_discount']) - Decimal(item['price'])

            yield item

    def __len__(self):
        return len(self.cart)

    def add(self, product, quantity):
        if product.is_available and quantity > 0:
            product_id = str(product.id)
            if product_id not in self.cart:
                self.cart[product_id] = {}
            self.cart[product_id]['product'] = product
            self.cart[product_id]['price_no_discount'] = product.price_no_discount
            self.cart[product_id]['price'] = str(product.price)
            self.cart[product_id]['quantity'] = self.cart.get(product_id, {}).get('quantity', 0) + quantity
            self.save()
            return True
        return False

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            return True
        return False

    def save(self):
        self.session.modified = True

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.save()