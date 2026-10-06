from django.urls import path

from admin_panel.views.website import (
    AdminWebsiteSettingView,

    AdminHomeBannerListView,
    AdminHomeBannerCreateView,
    AdminHomeBannerDetailView,
    AdminHomeBannerUpdateView,
    AdminHomeBannerDeleteView,

    AdminSecondaryBannerListView,
    AdminSecondaryBannerCreateView,
    AdminSecondaryBannerDetailView,
    AdminSecondaryBannerUpdateView,
    AdminSecondaryBannerDeleteView,

    AdminHomeCategoryListView,
    AdminHomeCategoryCreateView,
    AdminHomeCategoryDetailView,
    AdminHomeCategoryUpdateView,
    AdminHomeCategoryDeleteView,
)


urlpatterns = [

    # ======================================================
    # WEBSITE SETTING
    # ======================================================

    path(
        "settings/",
        AdminWebsiteSettingView.as_view(),
        name="admin-website-settings",
    ),


    # ======================================================
    # HOME BANNERS
    # ======================================================

    path(
        "banners/",
        AdminHomeBannerListView.as_view(),
        name="admin-home-banners",
    ),

    path(
        "banners/create/",
        AdminHomeBannerCreateView.as_view(),
        name="admin-home-banner-create",
    ),

    path(
        "banners/<int:pk>/",
        AdminHomeBannerDetailView.as_view(),
        name="admin-home-banner-detail",
    ),

    path(
        "banners/<int:pk>/update/",
        AdminHomeBannerUpdateView.as_view(),
        name="admin-home-banner-update",
    ),

    path(
        "banners/<int:pk>/delete/",
        AdminHomeBannerDeleteView.as_view(),
        name="admin-home-banner-delete",
    ),


    # ======================================================
    # SECONDARY BANNER
    # ======================================================

    path(
        "secondary-banners/",
        AdminSecondaryBannerListView.as_view(),
        name="admin-secondary-banners",
    ),

    path(
        "secondary-banners/create/",
        AdminSecondaryBannerCreateView.as_view(),
        name="admin-secondary-banner-create",
    ),

    path(
        "secondary-banners/<int:pk>/",
        AdminSecondaryBannerDetailView.as_view(),
        name="admin-secondary-banner-detail",
    ),

    path(
        "secondary-banners/<int:pk>/update/",
        AdminSecondaryBannerUpdateView.as_view(),
        name="admin-secondary-banner-update",
    ),

    path(
        "secondary-banners/<int:pk>/delete/",
        AdminSecondaryBannerDeleteView.as_view(),
        name="admin-secondary-banner-delete",
    ),


    # ======================================================
    # HOME CATEGORIES
    # ======================================================

    path(
        "categories/",
        AdminHomeCategoryListView.as_view(),
        name="admin-home-categories",
    ),

    path(
        "categories/create/",
        AdminHomeCategoryCreateView.as_view(),
        name="admin-home-category-create",
    ),

    path(
        "categories/<int:pk>/",
        AdminHomeCategoryDetailView.as_view(),
        name="admin-home-category-detail",
    ),

    path(
        "categories/<int:pk>/update/",
        AdminHomeCategoryUpdateView.as_view(),
        name="admin-home-category-update",
    ),

    path(
        "categories/<int:pk>/delete/",
        AdminHomeCategoryDeleteView.as_view(),
        name="admin-home-category-delete",
    ),

]

