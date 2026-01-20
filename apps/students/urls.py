from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentGroupViewSet, StudentViewSet, TeacherViewSet

app_name = 'students'

router = DefaultRouter()
router.register(r'groups', StudentGroupViewSet, basename='studentgroup')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),
]
