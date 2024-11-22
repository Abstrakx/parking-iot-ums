from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import mahasiswaViewSet, CustomLoginView
from .views import dashboard_mahasiswa_list, delete_mahasiswa, edit_mahasiswa
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'mahasiswa', mahasiswaViewSet)

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('dashboard/', dashboard_mahasiswa_list, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('delete-mahasiswa/', delete_mahasiswa, name='delete_mahasiswa'),
    path('edit-mahasiswa/', edit_mahasiswa, name='edit_mahasiswa'),
    path('api/', include(router.urls)),
]