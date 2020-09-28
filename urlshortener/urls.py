from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from urlshortener import views

urlpatterns = [
    path("", views.UrlView.as_view()),
    path('<str:url_hash>/', views.UrlRoot.as_view(), name='root'),
    path('stats/<url_id>', views.Stats.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
