from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import (
    Profile, Course, Quiz, ShopItem, PlayerProfile, Purchase,
    CompletedQuiz, LeaderboardEntry, Question, Option
)
from .forms import SignInForm

# DRF API ViewSetit
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    ProfileSerializer, CourseSerializer, PlayerProfileSerializer, ShopItemSerializer,
    PurchaseSerializer, QuizSerializer, QuestionSerializer, OptionSerializer,
    CompletedQuizSerializer, LeaderboardEntrySerializer
)

# 📦 HTML-based views (templates)

def home(request):
    courses = Course.objects.all()
    completed_courses = []

    if request.user.is_authenticated:
        player_profile = PlayerProfile.objects.get(user=request.user)
        completed_courses = Course.objects.filter(completedquiz__player=player_profile)

    return render(request, 'home.html', {
        'courses': courses,
        'completed_courses': completed_courses
    })


def course_list(request):
    courses = Course.objects.all().order_by('title')
    completed_course_ids = []

    if request.user.is_authenticated:
        player_profile = PlayerProfile.objects.get(user=request.user)
        completed_course_ids = CompletedQuiz.objects.filter(player=player_profile).values_list('course_id', flat=True)

    return render(request, 'course_list.html', {
        'courses': courses,
        'completed_course_ids': completed_course_ids,
    })


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'course_detail.html', {'course': course})


def course_search(request):
    query = request.GET.get('q')
    courses = Course.objects.filter(title__icontains=query) if query else Course.objects.all()
    return render(request, 'course_search.html', {'courses': courses, 'query': query})


@login_required(login_url='/login/')  # Use the correct login URL
def shop(request):
    player_profile, created = PlayerProfile.objects.get_or_create(user=request.user)
    shop_items = ShopItem.objects.all()
    return render(request, 'shop.html', {
        'player_profile': player_profile,
        'shop_items': shop_items
    })


@login_required
def buy_item(request, item_id):
    item = get_object_or_404(ShopItem, pk=item_id)
    player_profile = PlayerProfile.objects.get(user=request.user)
    if player_profile.points >= item.price:
        player_profile.points -= item.price
        player_profile.save()
        Purchase.objects.create(player=player_profile, item=item)
    else:
        messages.error(request, "You do not have enough points to buy this item.")
    return redirect('shop')


@login_required
def quiz_view(request, course_id, question_number=1):
    course = get_object_or_404(Course, pk=course_id)
    quiz = get_object_or_404(Quiz, course=course)
    questions = quiz.questions.all().order_by('id')
    total_questions = questions.count()
    points_per_correct = 50

    if 'score' not in request.session:
        request.session['score'] = 0

    if question_number > total_questions:
        score = request.session.get('score', 0)
        gained_points = score * points_per_correct

        if 'score' in request.session:
            del request.session['score']

        player_profile = PlayerProfile.objects.get(user=request.user)
        CompletedQuiz.objects.get_or_create(player=player_profile, course=course)

        return render(request, 'quiz_complete.html', {
            'course': course,
            'score': score,
            'total_questions': total_questions,
            'gained_points': gained_points,
        })

    question = questions[question_number - 1]

    if request.method == 'POST':
        selected_option_id = request.POST.get('selected_option')
        correct_option = question.options.filter(is_correct=True).first()

        if selected_option_id and correct_option and int(selected_option_id) == correct_option.id:
            request.session['score'] += 1
            player_profile = PlayerProfile.objects.get(user=request.user)
            player_profile.points += points_per_correct
            player_profile.save()

        return redirect('quiz', course_id=course.id, question_number=question_number + 1)

    return render(request, 'quiz.html', {
        'course': course,
        'quiz': quiz,
        'question': question,
        'current_question_number': question_number,
        'total_questions': total_questions,
    })


def create_profile(request):
    error_message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        birthdate = request.POST.get('birthdate')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            error_message = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error_message = 'Username already exists.'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            PlayerProfile.objects.create(user=user)
            return redirect('home')

    return render(request, 'create_profile.html', {'error_message': error_message})


@login_required
def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    player_profile = get_object_or_404(PlayerProfile, user=user)
    purchases = Purchase.objects.filter(player=player_profile)
    return render(request, 'view_profile.html', {
        'user_profile': user,
        'player_profile': player_profile,
        'purchases': purchases,
    })


def sign_in_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('course_list')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = SignInForm()

    return render(request, 'account/sign_in.html', {'form': form})


def complete_course(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        points_earned = int(request.POST.get('score', 0))
        entry, created = LeaderboardEntry.objects.get_or_create(name=name)
        entry.score += points_earned
        entry.save()
        return redirect('leaderboard')


def leaderboard(request):
    entries = LeaderboardEntry.objects.order_by('-score', 'name')
    return render(request, 'leaderboard.html', {'entries': entries})


# 📦 REST API ViewSets (DRF)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PlayerProfileViewSet(viewsets.ModelViewSet):
    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CompletedQuizViewSet(viewsets.ModelViewSet):
    queryset = CompletedQuiz.objects.all()
    serializer_class = CompletedQuizSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LeaderboardEntryViewSet(viewsets.ModelViewSet):
    queryset = LeaderboardEntry.objects.all()
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# View to show when user is not signed in
def not_signed_in(request):
    return render(request, 'not_signed_in.html')
