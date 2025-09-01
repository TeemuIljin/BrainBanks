from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# DRF API-reititin
router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'player-profiles', views.PlayerProfileViewSet)
router.register(r'shop-items', views.ShopItemViewSet)
router.register(r'purchases', views.PurchaseViewSet)
router.register(r'quizzes', views.QuizViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'options', views.OptionViewSet)
router.register(r'completed-quizzes', views.CompletedQuizViewSet)
router.register(r'leaderboard-entries', views.LeaderboardEntryViewSet)

urlpatterns = [
    # Home path is now handled by main URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('search/', views.course_search, name='course_search'),
    path('shop/', views.shop, name='shop'),
    path('shop/buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('quiz/<int:course_id>/<int:question_number>/', views.quiz_view, name='quiz'),
    path('login/', views.sign_in_view, name='sign_in'),
    path('complete-course/', views.complete_course, name='complete_course'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('not_signed_in/', views.not_signed_in, name='not_signed_in'),
]

