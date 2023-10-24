from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Book, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "username", "email", "password1", "password2"]


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"
        exclude = ["host", "participants"]

    def clean(self):
        cleaned_data = super().clean()
        # Example: Check the 'name' field and add an error if it's empty
        image = cleaned_data.get("image")
        if not image:
            self.add_error("image", "Name cannot be empty")


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "username", "name", "email", "bio"]
