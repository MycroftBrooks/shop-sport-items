from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import OrderSummaryView

urlpatterns = [
    path("", views.index, name="index"),
    path("catalog", views.catalogView, name="catalog"),
    path("product/<int:pk>/", views.CatalogDetailView, name="product"),
    path("DeleteProduct/<product_id>/", views.DeleteProduct, name="delete_product"),
    path("update_product/<product_id>/", views.update_product, name="update_product"),
    path("add_to_cart/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path(
        "remove_single_item_from_cart/<int:pk>/",
        views.remove_single_item_from_cart,
        name="remove_single_item_from_cart",
    ),
    path("order_summary/", OrderSummaryView.as_view(), name="order_summary"),
    path("about", views.about, name="about"),
    path("faq", views.faq, name="faq"),
    path("create", views.create, name="create"),
    path("login", views.login_user, name="login"),
    path("register", views.register_user, name="register"),
    path("logout", views.logout_user, name="logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
