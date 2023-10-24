from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),
    path("profile/<str:pk>/", views.userProfile, name="profile"),
    path("", views.home, name="home"),
    path("books/<str:pk>/", views.book, name="book"),
    path("create-book/", views.createBook, name="createbook"),
    path("update-book/<str:pk>", views.updateBook, name="updatebook"),
    path("delete-book/<str:pk>", views.deleteBook, name="deletebook"),
    path("delete-comment/<str:pk>", views.deleteComment, name="deletecomment"),
    path("update-user/<str:pk>", views.updateUser, name="updateuser"),
    path("topics/", views.topicPage, name="topics"),
]
