from django.urls import include, path
from treenipaivakirja import views
from treenipaivakirja import rest_api
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('', views.index, name='index'),
    path('trainings/', views.trainings_view, name='trainings'),
    path('trainings/add/', views.training_add, name='training_add'),
    path('trainings/<int:pk>/modify', views.training_modify, name='training_modify'),
    path('trainings/<int:pk>/delete', views.training_delete, name='training_delete'),
    path('trainings/data', views.trainings_data, name='trainings_data'),
    path('reports/amounts/', views.reports_amounts, name='reports_amounts'),
    path('reports/sports/', views.reports_sports, name='reports_sports'),
    path('reports/zones/', views.reports_zones, name='reports_zones'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('settings/', views.settings_view, name='settings'),
    path('register', views.register, name='register'),
    path('api/trainings', rest_api.trainings),
    path('api/trainings/<int:pk>', rest_api.trainings_by_id),
    path('api/token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
