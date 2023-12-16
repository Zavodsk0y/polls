from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import *

app_name = 'app'

urlpatterns = [
                  path('accounts/login/', BBLoginView.as_view(), name='login'),
                  path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
                  path('accounts/profile/<int:pk>/change/', ChangeUserInfoView.as_view(), name='profile_change'),
                  path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
                  path('accounts/profile/', profile, name='profile'),
                  path('accounts/signup/', SignUpView.as_view(), name='signup'),
                  path('accounts/delete/', DeleteUserView.as_view(), name='user_delete'),
                  path('', Index.as_view(), name='index'),
                  path('<int:pk>/', DetailPoll.as_view(), name='detail'),
                  path('<int:poll_id>/vote/', views.vote, name='vote'),
                  path('<int:pk>/results/', ResultsView.as_view(), name='results')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
