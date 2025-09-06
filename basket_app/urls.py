from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApiModelViewSet, BasketViewSet, BasketItemViewSet, basket_summary

router = DefaultRouter()
router.register(r'basket', ApiModelViewSet, basename='basket')
router.register(r'baskets', BasketViewSet, basename='basketlist')
router.register(r'basket-items', BasketItemViewSet, basename='basketitem')

urlpatterns = [
    path('', include(router.urls)),
    path('basket-summary/', basket_summary, name='basket-summary'),
    path('basket-summary/<int:basket_id>/', basket_summary, name='basket-summary-specific'),
]
