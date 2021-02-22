from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, BillingAddress
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckOutForm

class HomeView(ListView):
    template_name = 'home.html'
    model = Item
    context_object_name = 'items'
    paginate_by = 2

# def home(request):
#     items = Item.objects.all()
#     context = {'items': items}
#     return render(request, 'home.html', context)

class CheckOutView(View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data['street_address']
                apartment_address = form.cleaned_data['apartment_address']
                zip = form.cleaned_data['zip']
                country = form.cleaned_data['country']

                # Todo: add function for this
                # same_shipping_address = form.cleaned_data['same_billing_address']
                # save_info = form.cleaned_data['save_info']

                payment_option = form.cleaned_data['payment_option']
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # Todo: redirect to the payment method
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'You have no active item!')
            return redirect('core:order_summary')


        messages.warning(self.request, 'fail form')
        return redirect('core:checkout')

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')

# def product(request):
#     items = Item.objects.all()
#     context = {'items': items}
#     return render(request, 'product.html', context)

class OrderSummary(LoginRequiredMixin ,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                }
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, 'You have no item in cart!')
            return redirect('/')
        


class ItemDetailView(DetailView):
    template_name = 'product.html'
    context_object_name = 'item'
    model = Item

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    user = request.user
    order_item, created = OrderItem.objects.get_or_create(
        ordered=False,
        user=user,
        item=item,
    )
    order_qs = Order.objects.filter(user=user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if not created:
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was update!')
            return redirect('core:order_summary')

        else:
            order.items.add(order_item)
            messages.info(request, 'This item was added into your cart!')
            return redirect('core:order_summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'This item was added into your cart!')
        return redirect('core:order_summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    user = request.user
    order_item_qs = OrderItem.objects.filter(
        item=item,
        ordered=False,
        user=user,
        )
    if not order_item_qs.exists():
        messages.info(request, 'You do not have this item in cart!')
    else:
        order_item = order_item_qs[0]
        order = Order.objects.get(
            user=user,
            ordered=False,
        )
        order.items.remove(order_item)
        order_item.delete()
        messages.info(request, 'Successful remove item from cart')

    return redirect('core:product', slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    user = request.user
    order_item_qs = OrderItem.objects.filter(
        item=item,
        ordered=False,
        user=user,
        )

    if not order_item_qs.exists():
        messages.info(request, 'You do not have this item in cart!')

    else:
        order_item = order_item_qs[0]
        order = Order.objects.get(
            user=user,
            ordered=False,
        )
        order_item.quantity -= 1
        order_item.save()
        if order_item.quantity <= 0:
            order_item.delete()
            order.items.remove()

        messages.info(request, 'Successful update your cart!')
        return redirect('core:order_summary')
