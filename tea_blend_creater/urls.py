from django.contrib import admin
from django.urls import path
from main_functionality.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page),
    path('blend_creater/', tea_blend_creater_form),
    path('save/', save_blend),
    path('regenerate/', regenerate_blend),
    path('catalog/', catalog_view),
    path('blend/<int:blend_id>/', blend_detail),
    path('about/', about_view)
]
