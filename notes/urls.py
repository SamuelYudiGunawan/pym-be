from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    # API endpoints
    path('api/notes/', views.get_notes, name='get_notes'),
    path('api/notes/submit/', views.submit_note, name='submit_note'),
    path('api/notes/<int:note_id>/', views.get_note_detail, name='get_note_detail'),
    path('api/notes/<int:note_id>/replies/', views.submit_reply, name='submit_reply'),
    path('api/about/', views.about_api, name='about_api'),
    
    # Authentication endpoints
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/register/', views.register_view, name='register'),
    path('api/auth/user/', views.current_user, name='current_user'),
    
    # Monitoring test endpoints
    path('api/test/error-400/', views.test_error_400, name='test_error_400'),
    path('api/test/error-500/', views.test_error_500, name='test_error_500'),
    path('api/test/slow/', views.test_slow, name='test_slow'),
    path('api/test/rate-limiter/', views.test_rate_limiter, name='test_rate_limiter'),
    
    # Synchronization demonstration endpoints
    path('api/test/sync-demo/', views.sync_demo, name='sync_demo'),
    path('api/metrics/internal/', views.internal_metrics, name='internal_metrics'),
]