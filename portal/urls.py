from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
# router.register(r'books', BookListView)
# router.register(r'entries', PageEntryViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'memberships', GroupMembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('entries/', PageEntryView.as_view(), name='entry-list-create'),
    path('entries/<int:pk>/', EntryDetailView.as_view(), name='entry-detail'),
    path('group-list/', GroupListView.as_view(), name='group-list'),
    path('login/', TRLoginView.as_view(), name='tr-login'),
]
