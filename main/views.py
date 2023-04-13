from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView

from .forms import RegisterUserFrom, catalogForm
from .models import Order, OrderItem, catalog


# Create your views here.
def index(request):
    return render(request, "main/index.html")


def catalogView(request):
    catalog_list = catalog.objects.all()
    return render(
        request,
        "main/catalog.html",
        {"catalog_list": catalog_list},
    )


def about(request):
    return render(request, "main/about.html")


def faq(request):
    return render(request, "main/faq.html")


def CatalogDetailView(request, pk):
    product = catalog.objects.get(id=pk)
    return render(request, "main/product.html", {"product": product})


def create(request):
    submitted = False
    if request.method == "POST":
        form = catalogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/create?submitted=True")
    else:
        form = catalogForm
        if "submitted" in request.GET:
            submitted = True
    return render(request, "main/create.html", {"form": form, "submitted": submitted})


def DeleteProduct(request, product_id):
    product = catalog.objects.get(pk=product_id)
    product.delete()
    messages.info(request, "Товар успешно удален")
    return redirect("catalog")


def update_product(request, product_id):
    product = catalog.objects.get(pk=product_id)
    if request.method == "POST":
        form = catalogForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("catalog")
    else:
        form = catalogForm(instance=product)
    return render(request, "main/update_product.html", {"form": form})


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(catalog, id=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Количество товара обновлено")
        else:
            order.items.add(order_item)
            messages.info(request, "Товар добавлен в корзину")
            return redirect("order_summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Товар добавлен в корзину")
    return redirect("order_summary")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(catalog, id=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Товар удален из корзины")
            return redirect("order_summary")
        else:
            messages.info(request, "Нет этого товара в корзине")
            return redirect("order_summary", pk=pk)
    else:
        messages.info(request, "У вас нет активного заказа")
        return redirect("order_summary", pk=pk)


@login_required
def remove_single_item_from_cart(request, pk):
    item = get_object_or_404(catalog, id=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Колличество товара обновлено")
            return redirect("order_summary")
        else:
            messages.info(request, "Товар не в корзине")
            return redirect("product", pk=pk)
    else:
        messages.info(request, "У вас нет активного заказа")
        return redirect("product", pk=pk)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {"object": order}
            return render(self.request, "main/order_summary.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "У вас нет активного заказа")
            return redirect("/")


# Логика авторизации
def register_user(request):
    if request.method == "POST":
        form = RegisterUserFrom(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Вы зарегистрировались как " + username))
            return redirect("index")
    else:
        form = RegisterUserFrom()
    return render(request, "main/register.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.success(request, "Логин или пароль неверны")
            return render(request, "main/login.html")
    else:
        return render(request, "main/login.html")


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("Вы вышли из аккаунта"))
    return redirect("catalog")
