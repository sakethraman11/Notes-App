from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('notes/create/', views.create_note, name='create_note'),  
    path('notes/<int:id>/', views.get_note, name='get_note'),
    path('notes/share/', views.share_note),
    path('notes/update/<int:id>/', views.update_note, name='update_note'),
    path('notes/delete/<int:id>/', views.delete_note, name='delete_note'),  
    path('notes/version-history/<int:id>/', views.get_note_version_history),
    path('', views.home, name='home'),  # Redirect to home page for GET requests to root URL
]
