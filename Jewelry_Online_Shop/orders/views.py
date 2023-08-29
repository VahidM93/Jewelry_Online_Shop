from django.conf import settings
import requests
import json
import jsonpickle
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from .cart import Cart
from .forms import AddToCartForm, ChooseAddressApplyCouponForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem, Coupon
from customers.models import Customer
from django.utils.translation import gettext as _
from products.models import Product
from orders.tasks import send_order_status_email
from .models import Order


class CartView(View):
    def get(self, request):

        cart = Cart(request)
        for item in cart:
            if not item['product'].is_available:
                cart.remove(item['product'])

        if request.user.is_authenticated:
            customer = request.user.customer
            unpaid_orders = customer.orders.filter(is_paid=False)
        else:
            unpaid_orders = None

        return render(request, 'orders/cart.html', {'cart': cart, 'unpaid_orders': unpaid_orders})


class CartAddView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['quantity'] > product.stock:
                messages.error(request, _('You can not add more than {} to your cart').format(product.stock), 'danger')
                return redirect('products:product_details', slug=product.slug)
            else:
                messages.success(request, _('Product added to cart successfully'), 'success')
                cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')


class CartRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        for item in cart:
            if not item['product'].is_available:
                cart.remove(item['product'])

        customer = request.user.customer
        order = Order.objects.create(customer=customer)
        items_list = [OrderItem(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
                      for item in cart]
        print(items_list)
        OrderItem.objects.bulk_create(items_list)
        cart.clear()
        return redirect('orders:order_details', order.id)


class OrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        customer = get_object_or_404(Customer, user=request.user)
        order = Order.objects.filter(customer=customer, id=order_id)

        order = order.get()
        cart = Cart(request)

        order_items = OrderItem.objects.filter(order=order)

        for item in cart:
            # if item is not in order_items create an order_item for it
            if not order_items.filter(product=item['product']).exists():
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            # if item of cart in order_items: Update the quantity of the order_item
            elif order_items.filter(product=item['product']).exists():
                order_item = order_items.get(product=item['product'])
                order_item.quantity = item['quantity']
                order_item.save()

        # if there is an order_item which is not in cart items remove order_item
        for orderitem in order_items:
            product = orderitem.product
            if str(product.id) not in cart.cart:
                orderitem.delete()

        cart.clear()
        return redirect('orders:order_details', order.id)


class OrderDetailView(LoginRequiredMixin, View):
    form_class = ChooseAddressApplyCouponForm
    template_name = 'orders/order_details.html'

    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.order = get_object_or_404(Order, id=kwargs['order_id'])

        return super(OrderDetailView, self).setup(request, *args, **kwargs)

    def get(self, request, order_id):
        order = self.order
        form = self.form_class(request=request, order=order)
        if order.check_address():
            return render(request, self.template_name, {'order': order, 'form': form})
        return redirect('customers:address_create')

    def post(self, request, order_id):
        order = self.order
        form = self.form_class(request.POST, request=request, order=order)
        if form.is_valid():
            address = form.cleaned_data['address']
            phone_number = form.cleaned_data['phone_number']
            order.save_address(address, phone_number)
            if form.cleaned_data['coupon']:
                coupon = Coupon.objects.all().filter(code=form.cleaned_data['coupon'])
                if coupon.exists():
                    coupon = coupon.get()
                    if coupon.is_coupon_valid():
                        order.coupon = coupon
                        order.apply_coupon()
                        order.save()
                        messages.success(request, _('Coupon applied successfully'), 'info')
                    else:
                        messages.error(request, _('Coupon is not valid'), 'danger')
                else:
                    messages.error(request, _('Coupon not found'), 'danger')
            else:
                order.coupon = None
                order.discount = 0
                order.save()
            messages.info(request, _('Order Information saved successfully'), 'info')
            return redirect('orders:order_details', order.id)
        messages.error(request, _('Please correct the error below.'), 'danger')
        return render(request, self.template_name, {'order': order, 'form': form})


class OrderDeleteView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        messages.success(request, _('Order deleted successfully'), 'info')
        return redirect('orders:cart')



# ------------------------- Zarrin Pal Information --------------------------
    
if settings.SANDBOX:
        sandbox = "sandbox"
else:
    sandbox = "www"
    
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = (
    f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
)
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
description = _("Deja Online Shop")
CallbackURL = "http://127.0.0.1:8000/orders/verify/"

# class OrderPaymentView(View):
    # def get(self, request, order_id):
    #     order = Order.objects.get(id=order_id)
    #     request.session["order_pay"] = {
    #         "order_id": order.id,
    #     }
    #     data = {
    #         "MerchantID": settings.MERCHANT,
    #         "Amount": float(order.get_total_price()) * 1000,
    #         "Description": description,
    #         "CallbackURL": CallbackURL,
    #         "metadata": {"mobile": order.phone_number},
    #     }
    #     data = json.dumps(data)
    #     headers = {
    #         "accept": "application/json",
    #         "content-type": "application/json",
    #         "content-length": str(len(data)),
    #     }
    #     try:
    #         response = requests.post(
    #             ZP_API_REQUEST, data=data, headers=headers, timeout=10
    #         )
    #         if response.status_code == 200:
    #             response = response.json()
    #             if response["Status"] == 100:
    #                 return redirect(ZP_API_STARTPAY + str(response["Authority"]))
    #             elif response.get("errors"):
    #                 e_code = response["errors"]["code"]
    #                 e_message = response["errors"]["message"]
    #                 return HttpResponse(
    #                     f"Error code: {e_code}, Error Message: {e_message}"
    #                 )
    #         return HttpResponse(response.items())

    #     except requests.exceptions.Timeout:
    #         return {"status": False, "code": "timeout"}
    #     except requests.exceptions.ConnectionError:
    #         return {"status": False, "code": "connection error"}
class OrderPaymentView(View):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            # Handle the case where the order does not exist
            messages.error(request, 'Invalid order ID')
            return redirect('accounts:user_profile')

        request.session["order_pay"] = {
            "order_id": order.id,
        }
        
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": int(round(float(order.get_total_price()))) * 1000,
            "Description": description,
            "CallbackURL": CallbackURL,
            "metadata": {"mobile": order.phone_number},
        }
        data = json.dumps(data)
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "content-length": str(len(data)),
        }
        try:
            response = requests.post(
                ZP_API_REQUEST, data=data, headers=headers, timeout=10
            )
            if response.status_code == 200:
                response = response.json()
                if response["Status"] == 100:
                    return redirect(ZP_API_STARTPAY + str(response["Authority"]))
                elif response.get("errors"):
                    e_code = response["errors"]["code"]
                    e_message = response["errors"]["message"]
                    return HttpResponse(
                        f"Error code: {e_code}, Error Message: {e_message}"
                    )
            return HttpResponse(response.items())

        except requests.exceptions.Timeout:
            return {"status": False, "code": "timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": False, "code": "connection error"}


class OrderVerifyView(View):
    def get(self, request):
        # Check if 'order_pay' key exists in the session
        order_pay_data = request.session.get('order_pay', None)

        if order_pay_data is not None:
            # The 'order_pay' key exists in the session
            order_id = order_pay_data.get('order_id')
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                # Handle the case where the order does not exist
                messages.error(request, 'Invalid order ID')
                return redirect('accounts:user_profile')

            data = {
                "MerchantID": settings.MERCHANT,
                "Amount": int(round(float(order.get_total_price()))) * 1000,
                "Authority": request.GET["Authority"],
            }
            data = jsonpickle.encode(data)  # Use jsonpickle.encode() for serialization
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "content-length": str(len(data)),
            }

            response = requests.post(ZP_API_VERIFY, data=data, headers=headers)
            if response.status_code == 200:
                response = response.json()
                if response["Status"] == 100 or response["Status"] == 101:
                    order.status = 2
                    order.transaction_id = response["RefID"]
                    order.is_paid = True
                    order.save()

                    if order.coupon:
                        coupon = order.coupon
                        coupon.is_active = False
                        coupon.save()
                        order.coupon = None
                        order.save()

                    items = order.items.all()
                    product_ids = [item.product.id for item in items]
                    products = Product.objects.all().filter(id__in=product_ids)
                    for item in items:
                        product = products.get(id=item.product.id)
                        product.stock -= item.quantity
                        product.save()

                    if order.customer.user.email:
                        mail = order.customer.user.email
                        message = f"Transaction success.RefID:  {str(response['RefID'])}"
                        mail_subject = "Order Confirmed Successfully"
                        send_order_status_email.delay(mail, message, mail_subject)

                    message = f"Transaction success.RefID:  {str(response['RefID'])}, Status: {response['Status']}, order ID: {order_id}"
                    return redirect('accounts:user_profile')
                else:
                    order.status = 3
                    order.save()
                    message = f"Transaction failed, order ID:" + str(order_id)
            return redirect('accounts:user_profile')

        # Handle the case where 'order_pay' is not in the session
        messages.error(request, 'No order payment data found in the session')
        return redirect('accounts:user_profile')


# class OrderPaymentView(LoginRequiredMixin, View):
#     def get(self, request, order_id):
#         order = get_object_or_404(Order, id=order_id)
#         address = (order.city, order.body, order.postal_code, order.phone_number)
#         if not all(address):
#             messages.error(request, _('You must provide an address'), 'danger')
#             return redirect('orders:order_details', order.id)

#         items = order.items.all()
#         count_of_removed_product = 0
#         for item in items:
#             if not item.product.is_available:
#                 item.delete()
#                 count_of_removed_product += 1

#         if count_of_removed_product > 0:
#             messages.error(request, _('Some of your items are sold out check your order'), 'danger')
#             return redirect('orders:order_details', order.id)

#         request.session['order_pay'] = {
#             'order_id': order.id,
#         }
#         req_data = {
#             "merchant_id": settings.MERCHANT,
#             "amount": order.get_total_price(),
#             "callback_url": CallbackURL,
#             "description": description,
#             "metadata": {"mobile": request.user.phone_number, "email": request.user.email}
#         }
#         req_header = {"accept": "application/json", "content-type": "application/json"}
#         print(json.dumps(req_data))
#         req = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
#         authority = req_data.get('data')
#         print('****************',authority,'*********************')
#         if len(req.json()['errors']) == 0:
#             return redirect(ZP_API_STARTPAY.format(authority=authority))
#         else:
#             e_code = req.json()['errors']['code']
#             e_message = req.json()['errors']['message']
#             return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


# class OrderVerifyView(LoginRequiredMixin, View):
#     def get(self, request):
#         order_id = request.session['order_pay']['order_id']
#         order = Order.objects.get(id=int(order_id))
#         t_status = request.GET.get('Status')
#         t_authority = request.GET['Authority']
#         if request.GET.get('Status') == 'OK':
#             req_header = {"accept": "application/json",
#                           "content-type": "application/json"}
#             req_data = {
#                 "merchant_id": settings.MERCHANT,
#                 "amount": order.get_total_price(),
#                 "authority": t_authority
#             }
#             req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
#             if len(req.json()['errors']) == 0:
#                 t_status = req.json()['data']['code']
#                 if t_status == 100:
#                     order.is_paid = True
#                     order.save()

#                     if order.coupon:
#                         order.coupon.deactivate()

#                     items = order.items.all()
#                     product_ids = [item.product.id for item in items]
#                     products = Product.objects.get_active_list().filter(id__in=product_ids)
#                     for item in items:
#                         product = products.get(id=item.product.id)
#                         product.stock -= item.quantity
#                         product.save()

#                     order.transaction_code = str(req.json()['data']['ref_id'])
#                     order.save()
#                     messages.success(request, _('Transaction success.\nRefID: ') + str(req.json()['data']['ref_id']))
#                     return redirect('accounts:user_profile')
#                 elif t_status == 101:
#                     return HttpResponse('Transaction submitted : ' + str(req.json()['data']['message']))
#                 else:
#                     return HttpResponse('Transaction failed.\nStatus: ' + str(req.json()['data']['message']))
#             else:
#                 e_code = req.json()['errors']['code']
#                 e_message = req.json()['errors']['message']
#                 # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
#                 messages.error(request, _('Error code: ') + e_code + _("Error Message: ") + e_message)
#                 return redirect('accounts:user_profile')
#         else:
#             return HttpResponse('Transaction failed or canceled by user')