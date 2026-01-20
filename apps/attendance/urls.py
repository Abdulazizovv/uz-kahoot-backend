from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduleViewSet, LessonViewSet, AttendanceViewSet, AttendanceStatisticsViewSet

app_name = 'attendance'

router = DefaultRouter()
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'attendance-statistics', AttendanceStatisticsViewSet, basename='attendance-statistics')

urlpatterns = [
    path('', include(router.urls)),
]
