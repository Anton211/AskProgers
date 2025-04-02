from django.urls import path
from app import views


urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.popular, name='popular'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tag/<str:tag>/', views.tag_questions, name='tag'),
    path('ask/', views.create_question, name='ask'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('settings', views.settings, name='settings'),
]