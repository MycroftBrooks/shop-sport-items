from django.conf import settings
from django.db import models
from django.urls import reverse

CATEGORY_CHOICES = (
    ("Рубашка", "Рубашка"),
    ("Штаны", "Штаны"),
    ("Кофта", "Кофта"),
    ("Трусы", "Трусы"),
    ("Кепка", "Кепка"),
    ("Шорты", "Шорты"),
    ("Куртка", "Куртка"),
    ("Шапка", "Шапка"),
)

SEX_CHOICES = (("M", "Для мужчин"), ("W", "Для женщин"))

SIZE_CHOICES = (
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)


class catalog(models.Model):
    name = models.CharField("Название товара", max_length=100)
    category = models.CharField("Категория", choices=CATEGORY_CHOICES)
    sex = models.CharField("Пол", choices=SEX_CHOICES, max_length=1)
    size = models.CharField("Размер", choices=SIZE_CHOICES, max_length=3)
    price = models.FloatField()
    image = models.ImageField(blank=True, upload_to="products/")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product", kwargs={"pk": self.pk})

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={"pk": self.pk})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={"pk": self.pk})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(catalog, on_delete=models.CASCADE)
    quantity = models.IntegerField("Количество", default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_final_price(self):
        return self.get_total_item_price

    def get_quantity(self):
        return self.quantity


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

    def __str__(self):
        return self.user.username
