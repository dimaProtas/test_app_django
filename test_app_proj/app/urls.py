from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('head_index', views.head_index, name='head_index'),
    path('test/<int:survey_id>/<int:question_index>/', views.get_next_question, name='questions'),
    path('child_question/<int:survey_id>/<int:child_id>/<int:question_index>/', views.get_child_auestion, name='child_question'),
    path('save_questions/', views.save_questions),
    path('login/', views.MyLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/head_index'), name='logout'),
]
