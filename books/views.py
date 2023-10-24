from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Book, Topic, Comment, User
from .forms import BookForm, UserForm, MyUserCreationForm
from django.contrib import messages

# Create your views here.


def loginUser(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist.")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Password is incorrect.")

    context = {"page": page}
    return render(request, "books/register-user.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerUser(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An Error Occurred")

    return render(request, "books/register-user.html", {"form": form})


def home(request):
    q = request.GET.get("q", "")

    books = Book.objects.filter(
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        | Q(description__icontains=q)
        | Q(author__icontains=q)
    )
    topics = Topic.objects.all()
    book_count = books.count()
    authors = Book.objects.only("author").distinct()

    context = {
        "books": books,
        "topics": topics,
        "book_count": book_count,
        "authors": authors,
    }
    return render(request, "books/home.html", context)


def book(request, pk):
    book = Book.objects.get(id=pk)
    comments = book.comment_set.all().order_by("-created")
    if request.user.is_authenticated:
        book.participants.add(request.user)

    if request.method == "POST":
        comment = Comment.objects.create(
            user=request.user, book=book, body=request.POST.get("body")
        )
        return redirect("book", pk=book.id)

    mostRead = Book.objects.annotate(participants_count=Count("participants")).order_by(
        "-participants_count"
    )
    participants = book.participants.all()
    readers = participants.count()
    context = {
        "book": book,
        "comments": comments,
        "readers": readers,
        "mostRead": mostRead[:15],
    }

    return render(request, "books/book.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    books = Book.objects.filter(participants=user)

    mostRead = Book.objects.annotate(participants_count=Count("participants")).order_by(
        "-participants_count"
    )
    context = {"user": user, "books": books, "mostRead": mostRead}
    return render(request, "books/profile.html", context)


@login_required(login_url="login")
def createBook(request):
    topics = Topic.objects.all()
    form = BookForm()

    if not request.user.is_superuser:  # check if not admin go home
        return redirect("home")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Book.objects.create(
            host=request.user,
            topic=topic,
            author=request.POST.get("author"),
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            year=request.POST.get("year"),
            image=request.FILES.get("image"),
        )
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "books/book_form.html", context)


@login_required(login_url="login")
def updateBook(request, pk):
    topics = Topic.objects.all()
    book = Book.objects.get(id=pk)
    form = BookForm(instance=book)

    if not request.user.is_superuser:  # check if not the host say \/
        return redirect("home")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        book.name = request.POST.get("name")
        book.author = request.POST.get("author")
        book.topic = topic
        book.description = request.POST.get("description")
        book.year = request.POST.get("year")
        book.image = request.FILES.get("image")
        book.save()

        return redirect("home")

    context = {"form": form, "topics": topics, "book": book}
    return render(request, "books/book_form.html", context)


@login_required(login_url="login")
def deleteBook(request, pk):
    book = Book.objects.get(id=pk)

    if not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        book.delete()
        return redirect("home")

    return render(request, "books/delete.html", {"obj": book})


@login_required(login_url="login")
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    book = comment.book

    if request.user != comment.user:
        return redirect("home")

    if request.method == "POST":
        comment.delete()
        return redirect("book", pk=book.id)

    return render(request, "books/delete.html", {"obj": comment})


@login_required(login_url="login")
def updateUser(request, pk):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", pk=user.id)

    context = {"form": form}
    return render(request, "books/update_user.html", context)


def topicPage(request):
    topics = Topic.objects.all()
    books = Book.objects.all()
    context = {"topics": topics, "books": books}
    return render(request, "books/topics.html", context)
