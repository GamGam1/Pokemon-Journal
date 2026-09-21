from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, JournalEntryViewSet

router = DefaultRouter()
router.register(r'entries', JournalEntryViewSet, basename='entry')

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('', include(router.urls)),
]