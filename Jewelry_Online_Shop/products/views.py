from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Category, Comment
from .forms import ProductSearchForm, AddCommentForm
from orders.forms import AddToCartForm
from django.contrib import messages
from core.manager import *
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class LandingPageView(View):
    def get(self, request):
        return render(request, 'product/landing.html')


class HomeView(View):
    form_class = ProductSearchForm

    def get(self, request, category_slug=None):
        products = Product.objects.all() 
        if request.GET.get('search'):
            products = products.filter(name__contains=request.GET['search'])

        categories = Category.objects.all().filter(is_sub=False)
        if category_slug == 'all':
            pass
        elif category_slug:
            category = Category.objects.all().get(slug=category_slug)
            products = products.filter(category=category)
        return render(request, 'product/index.html',
                      {'products': products, 'categories': categories, 'form': self.form_class})


class ProductDetailsView(View):
    form_add = AddToCartForm
    form_comment = AddCommentForm
    template_name = 'product/details.html'

    def setup(self, request, *args, **kwargs):
        self.product = Product.objects.get(slug=kwargs['slug'])
        self.properties = self.product.properties.all()
        self.comments = self.product.pcomments.all()
        return super().setup(request, *args, **kwargs)

    def get(self, request, slug):
        product = self.product
        properties = self.properties
        comments = self.comments
        return render(request, self.template_name, {'product': product, 'properties': properties, 'form': self.form_add,
                                                    'form_comment': self.form_comment, 'comments': comments})


    @method_decorator(login_required)
    def post(self, request, slug):
        form_comment = self.form_comment(request.POST)
        if form_comment.is_valid():
            cd = form_comment.cleaned_data
            comment = Comment.objects.create(
                customer=request.user.customer,
                product=self.product,
                title=cd['title'],
                body=cd['comment'],
                # is_active=False,
            )
            messages.success(request, _('Comment added successfully'), 'info')
            return redirect('products:product_details', slug=slug)
        messages.error(request, _('Something went wrong. Check the possible errors'), 'danger')
        return render(request, self.template_name, {'form_comment': form_comment, 'products': self.product,
                                                    'properties': self.properties, 'comments': self.comments})
