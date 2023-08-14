from django.shortcuts import render
from django.views import View
from products.forms import ProductSearchForm
from .models import Category, Product


class HomeView(View):
    form_class = ProductSearchForm

    def get(self, request, category_slug=None):
        products = Product.objects.get_active_list().all()  # gets all objects that are active
        if request.GET.get('search'):
            products = products.filter(name__contains=request.GET['search'])

        categories = Category.objects.get_active_list().filter(is_sub=False)
        if category_slug == 'all':
            pass
        elif category_slug:
            category = Category.objects.get_active_list().get(slug=category_slug)
            products = products.filter(category=category)
        return render(request, 'products/index.html',
                      {'products': products, 'categories': categories, 'form': self.form_class})



class ProductDetailsView(View):
    def get(self, request, slug):
        product = Product.objects.get_active_list().get(slug=slug)
        properties = product.properties.all()
        return render(request, 'products/details.html', {'product': product, 'properties': properties})
    
    
    
class LandingPageView(View):
    def get(self, request):
        return render(request, 'products/landing.html')