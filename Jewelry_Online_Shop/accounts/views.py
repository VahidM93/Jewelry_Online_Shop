from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm, UserLoginForm, UserProfileForm
from core.utils import random_code, send_otp_code
from .models import OtpCode, Account
from django.contrib import messages
from customers.models import Customer, Address
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if OtpCode.is_code_available(phone_number=cd['phone']):
                rand_code = random_code()
                print(rand_code)
                send_otp_code(cd['phone'], rand_code)
                #save code with phone
                OtpCode.objects.create(phone_number=cd['phone'], code=rand_code)
                #save inputed data in session
                request.session['user_registration_info'] = {
                    'phone_number': cd['phone'],
                    'email': cd['email'],
                    'full_name': cd['full_name'],
                    'password': cd['password'],
                }
                messages.success(request, _('Code will be sent in minutes.'), 'success')
                return redirect('accounts:verify_code')
            else:
                messages.error(request, _('Too many attempts. Please Try again 20 minutes later.'), 'danger')
                return redirect('product:home')
        return render(request, self.template_name, {'form': form})


class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_registration_info']
        codes = OtpCode.objects.filter(phone_number=user_session['phone_number'])
        code_instance = codes.last()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code == code_instance.code:
                print(code)
                if code_instance.is_valid():
                    user = Account.objects.create_user(
                        phone_number=user_session['phone_number'],
                        email=user_session['email'],
                        full_name=user_session['full_name'],
                        password=user_session['password']
                    )
                    codes.delete()
                    messages.success(request, _('information has registered successfully'), 'success')
                    login(request, user)
                    return redirect('product:home')
                else:
                    messages.error(request, _('The code has expired. Please try again.'), 'danger')
                    return redirect('accounts:user_register')
            else:
                messages.error(request, _('WRONG Code!'), 'danger')
                return redirect('accounts:verify_code')
        return redirect('product:home')


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect('product:home')
    #     return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, phone_number=cd['phone'], password=cd['password'])
            if user:
                login(request, user)
                messages.success(request, _('logged in successfully'), 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('product:home')
            messages.error(request, _('Phone number or Password is WRONG!'), 'danger')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, _('logged out successfully'), 'info')
        return redirect('home:home')

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class UserProfileView(LoginRequiredMixin, View):
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'

    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
            self.customer = request.user.customer
            self.addresses = Address.objects.filter(customer=self.customer)
            self.unpaid_orders = self.customer.orders.filter(is_paid=False)
            self.paid_orders = self.customer.orders.filter(is_paid=True)
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class(
            instance=self.customer,
            initial={'full_name': self.user.full_name, 'email': self.user.email,
                     'phone_number': self.user.phone_number})
        return render(
            request, self.template_name, {'form': form, 'customer': self.customer, 'addresses': self.addresses,
                                          'unpaid_orders': self.unpaid_orders, 'paid_orders': self.paid_orders})

    def post(self, request):
        form = self.form_class(request.POST, files=request.FILES, instance=self.customer)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            self.user.full_name = cd['full_name']
            self.user.email = cd['email']
            self.user.phone_number = cd['phone_number']
            self.user.save()
            messages.success(request, _('Your information has updated successfully'), 'success')
            return redirect('accounts:user_profile')

        messages.error(request, _('Something went wrong. Correct the mistakes and try again.'), 'danger')
        return render(
            request, self.template_name,
            {'form': form, 'image': self.customer.image, 'customer': self.customer, 'addresses': self.addresses}
        )


class UserClearImageView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        customer = Customer.objects.get(user=user)
        customer.image = None
        customer.save()
        return redirect('accounts:user_profile')