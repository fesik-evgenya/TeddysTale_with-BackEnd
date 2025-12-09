from django.urls import path
from . import views_custom

app_name = 'teddy_admin_custom'

urlpatterns = [
    # Все пути внутри кастомной админки (префикс admin-custom/)
    path('enter/', views_custom.custom_admin_login, name='custom-login'),
    path('panel/', views_custom.custom_admin_panel, name='custom-panel'),
    path('logout/', views_custom.custom_admin_logout, name='custom-logout'),
    path('ajax/update-shop-item/<int:item_id>/', views_custom.update_shop_item_ajax, name='update-shop-item'),
    path('ajax/update-section/<str:section_key>/', views_custom.update_section_content_ajax, name='update-section'),
    path('ajax/upload-image/', views_custom.upload_image_ajax, name='upload-image'),
    path('ajax/upload-shop-item-image/<int:item_id>/', views_custom.upload_shop_item_image_ajax, name='upload-shop-item-image'),
    path('ajax/update-site-settings/', views_custom.update_site_settings_ajax, name='update-site-settings'),
]