from django.urls import path
from django.contrib.auth import views
from . import views
from django.conf.urls import include


urlpatterns = [
    path("follow/", views.follow_index, name="follow_index"),
    path('new/', views.new_post, name='new_post'),
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    path("", views.index, name="index"),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    path('la/stats/', views.stats, name='stats'),
    path('signup/', include("django.contrib.auth.urls"), name='users'),
    path("<str:username>/<int:post_id>/comment",
         views.add_comment, name="add_comment"),
    path("<str:username>/follow/",
         views.profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow, name="profile_unfollow"),
    path("404", views.page_not_found),
    path("500", views.server_error),
]
