from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import (
    Profile, Course, Quiz, ShopItem, PlayerProfile, Purchase,
    CompletedQuiz, LeaderboardEntry, Question, Option
)
from datetime import date, timedelta
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
    # Optimize: Only fetch courses that are needed for display
    courses = Course.objects.all()[:6]  # Limit to 6 courses for home page
    completed_courses = []
    player_profile = None

    if request.user.is_authenticated:
        try:
            # Use get_or_create to handle missing PlayerProfile gracefully
            player_profile, created = PlayerProfile.objects.get_or_create(user=request.user)
            # Optimize: Use select_related to reduce queries
            completed_courses = Course.objects.filter(
                completedquiz__player=player_profile
            ).select_related('quiz')
        except Exception as e:
            # Log error and continue without breaking the page
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching player profile for user {request.user.id}: {e}")

    context = {
        'courses': courses, 
        'completed_courses': completed_courses,
        'player_profile': player_profile
    }
    return render(request, 'home.html', context)


def course_list(request):
    # Optimize: Use select_related for better performance
    courses = Course.objects.select_related('quiz').order_by('title')
    completed_course_ids = []
    player_profile = None

    if request.user.is_authenticated:
        try:
            player_profile, created = PlayerProfile.objects.get_or_create(user=request.user)
            # Optimize: Use values_list to get only course IDs
            completed_course_ids = list(CompletedQuiz.objects.filter(
                player=player_profile
            ).values_list('course_id', flat=True))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching course list data for user {request.user.id}: {e}")

    context = {
        'courses': courses, 
        'completed_course_ids': completed_course_ids,
        'player_profile': player_profile
    }
    return render(request, 'course_list.html', context)


def course_detail(request, pk):
    # Optimize: Use select_related and prefetch_related for better performance
    course = get_object_or_404(
        Course.objects.select_related('quiz').prefetch_related('quiz__questions__options'),
        pk=pk
    )
    context = {'course': course}
    
    if request.user.is_authenticated:
        try:
            player_profile, created = PlayerProfile.objects.get_or_create(user=request.user)
            context['player_profile'] = player_profile
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching player profile for course detail: {e}")
    
    return render(request, 'course_detail.html', context)


def course_search(request):
    query = request.GET.get('q')
    courses = Course.objects.filter(title__icontains=query) if query else Course.objects.all()
    context = {'courses': courses, 'query': query}
    if request.user.is_authenticated:
        try:
            context['player_profile'] = PlayerProfile.objects.get(user=request.user)
        except PlayerProfile.DoesNotExist:
            pass
    return render(request, 'course_search.html', context)


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
    # Validate item_id is a positive integer
    try:
        item_id = int(item_id)
        if item_id <= 0:
            raise ValueError("Invalid item ID")
    except (ValueError, TypeError):
        messages.error(request, "Invalid item selected.")
        return redirect('shop')
    
    item = get_object_or_404(ShopItem, pk=item_id)
    
    try:
        player_profile, created = PlayerProfile.objects.get_or_create(user=request.user)
        
        # Check if user already owns this item
        if Purchase.objects.filter(player=player_profile, item=item).exists():
            messages.warning(request, "You already own this item.")
            return redirect('shop')
        
        if player_profile.points >= item.price:
            # Use atomic transaction to prevent race conditions
            from django.db import transaction
            with transaction.atomic():
                player_profile.points -= item.price
                player_profile.save()
                Purchase.objects.create(player=player_profile, item=item)
            messages.success(request, f"Successfully purchased {item.name}!")
        else:
            messages.error(request, "You do not have enough points to buy this item.")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error purchasing item {item_id} for user {request.user.id}: {e}")
        messages.error(request, "An error occurred while processing your purchase.")
    
    return redirect('shop')


@login_required
def quiz_view(request, course_id, question_number=1):
    # Optimize: Use select_related and prefetch_related for better performance
    course = get_object_or_404(Course.objects.select_related('quiz'), pk=course_id)
    quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__options'), course=course)
    
    # Optimize: Get questions with options in one query
    questions = quiz.questions.select_related().prefetch_related('options').order_by('id')
    total_questions = questions.count()
    points_per_correct = 50

    if 'score' not in request.session:
        request.session['score'] = 0

    if question_number > total_questions:
        score = request.session.get('score', 0)
        gained_points = score * points_per_correct

        if 'score' in request.session:
            del request.session['score']

        try:
            player_profile, created = PlayerProfile.objects.get_or_create(user=request.user)
            CompletedQuiz.objects.get_or_create(player=player_profile, course=course)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in quiz completion for user {request.user.id}: {e}")
            messages.error(request, "An error occurred while saving your progress.")
            return redirect('course_detail', pk=course_id)

        # Streak handling: increment if last activity was yesterday or today; reset otherwise
        today = date.today()
        if player_profile.last_activity_date in (today, today - timedelta(days=1)):
            player_profile.current_streak = (player_profile.current_streak or 0) + 1
        else:
            player_profile.current_streak = 1
        if player_profile.current_streak > (player_profile.longest_streak or 0):
            player_profile.longest_streak = player_profile.current_streak
        player_profile.last_activity_date = today
        player_profile.save()
        
        # Update leaderboard with new points
        update_leaderboard_entry(player_profile)

        return render(request, 'quiz_complete.html', {
            'course': course,
            'score': score,
            'total_questions': total_questions,
            'gained_points': gained_points,
            'player_profile': player_profile,
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
            # Update leaderboard immediately when points are earned
            update_leaderboard_entry(player_profile)

        return redirect('quiz', course_id=course.id, question_number=question_number + 1)

    return render(request, 'quiz.html', {
        'course': course,
        'quiz': quiz,
        'question': question,
        'current_question_number': question_number,
        'total_questions': total_questions,
        'player_profile': PlayerProfile.objects.get(user=request.user),
    })


def create_profile(request):
    error_message = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        birthdate = request.POST.get('birthdate', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Input validation
        if not username or len(username) < 3:
            error_message = 'Username must be at least 3 characters long.'
        elif not email or '@' not in email:
            error_message = 'Please enter a valid email address.'
        elif not password or len(password) < 8:
            error_message = 'Password must be at least 8 characters long.'
        elif password != confirm_password:
            error_message = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error_message = 'Username already exists.'
        elif User.objects.filter(email=email).exists():
            error_message = 'Email address is already registered.'
        else:
            try:
                # Use atomic transaction to ensure data consistency
                from django.db import transaction
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username, 
                        email=email, 
                        password=password
                    )
                    PlayerProfile.objects.create(user=user)
                messages.success(request, 'Profile created successfully!')
                return redirect('home')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating profile: {e}")
                error_message = 'An error occurred while creating your profile. Please try again.'

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
    from .utils import get_cached_leaderboard, set_cached_leaderboard
    
    # Try to get cached leaderboard data
    cached_data = get_cached_leaderboard()
    if cached_data:
        entries, user_position, total_players = cached_data
    else:
        # Sync leaderboard with current PlayerProfile data
        sync_leaderboard()
        entries = LeaderboardEntry.objects.order_by('-score', 'name')
        
        # Find current user's position if logged in
        user_position = None
        if request.user.is_authenticated:
            try:
                user_entry = entries.filter(name=request.user.username).first()
                if user_entry:
                    user_position = list(entries).index(user_entry) + 1
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error finding user position in leaderboard: {e}")
        
        total_players = entries.count()
        
        # Cache the result
        set_cached_leaderboard((entries, user_position, total_players))
    
    return render(request, 'leaderboard.html', {
        'entries': entries,
        'user_position': user_position,
        'total_players': total_players
    })


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


def update_leaderboard_entry(player_profile):
    """Update or create leaderboard entry for a player profile"""
    if player_profile.points > 0:
        entry, created = LeaderboardEntry.objects.get_or_create(
            name=player_profile.user.username,
            defaults={'score': 0}
        )
        # Update score to match current points
        if entry.score != player_profile.points:
            entry.score = player_profile.points
            entry.save()


def sync_leaderboard():
    """Sync leaderboard entries with current PlayerProfile data"""
    for profile in PlayerProfile.objects.all():
        if profile.points > 0:  # Only include users with points
            entry, created = LeaderboardEntry.objects.get_or_create(
                name=profile.user.username,
                defaults={'score': 0}
            )
            # Update score to match current points
            if entry.score != profile.points:
                entry.score = profile.points
                entry.save()
    
    # Remove entries for users who no longer exist or have 0 points
    LeaderboardEntry.objects.exclude(
        name__in=PlayerProfile.objects.filter(points__gt=0).values_list('user__username', flat=True)
    ).delete()
