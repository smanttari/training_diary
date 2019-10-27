from django.urls import include,path
from treenipaivakirja import views
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('', views.index, name='index'),
    path('trainings/', views.trainings_view, name='trainings'),
    path('trainings/add/', views.training_add, name='training_add'),
    path('trainings/<int:pk>/modify', views.training_modify, name='training_modify'),
    path('trainings/<int:pk>/delete', views.training_delete, name='training_delete'),
    path('trainings/data', views.trainings_data, name='trainings_data'),
    path('sports/add', views.sport_add, name='sport_add'),
    path('sports/<int:pk>/modify', views.sport_modify, name='sport_modify'),
    path('sports/<int:pk>/delete', views.sport_delete, name='sport_delete'),
    path('reports/', views.reports, name='reports'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('zones/add/', views.zone_add, name='zone_add'),
    path('zones/<int:pk>/modify', views.zone_modify, name='zone_modify'),
    path('zones/<int:pk>/delete', views.zone_delete, name='zone_delete'),
    path('settings/', views.settings_view, name='settings'),
    path('register', views.register, name='register'),
    path('api/trainings', views.trainings_api),
    path('api/trainings/<int:pk>', views.trainings_api_by_id),
    path('api/token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
