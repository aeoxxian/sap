from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from .views import (
    parent_login, parent_signup, parent_dashboard, parent_logout,
    get_field_definitions, exam_detail, exam_chart_data, exam_chart_all_data,
    download_exam_pdf
)

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='parent_login', permanent=False), name='home'),
    path('upload/', views.upload_csv, name='csv_upload'),
    path("parent/login/", parent_login, name="parent_login"),
    path("parent/signup/", parent_signup, name="parent_signup"),
    path("parent/dashboard/", parent_dashboard, name="parent_dashboard"),
    path("parent/logout/", parent_logout, name="parent_logout"),
    path("api/get_field_definitions/", get_field_definitions, name="get_field_definitions"),
    path("api/exam_chart/", exam_chart_data, name="exam_chart_data"),
    path("api/exam_chart_all/", exam_chart_all_data, name="exam_chart_all_data"),
    path("parent/student/<int:student_id>/exam/<int:exam_id>/", exam_detail, name="exam_detail"),
    path("parent/student/exam/<int:exam_id>/pdf/", download_exam_pdf, name="download_exam_pdf"),
    path("parent/student/<int:student_id>/all_exams/", views.all_exams_view, name="all_exams_view"),
    path("parent/student/<int:student_id>/all_assignments/", views.all_assignments_view, name="all_assignments_view"),
    path('chaining/', include('smart_selects.urls')),
]
