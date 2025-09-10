# courses/admin.py
from django.contrib import admin
from .models import Course, ShopItem, PlayerProfile, Purchase, Quiz, Question, Option

# Course admin with custom display
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'duration')
    fields = ('title', 'description', 'duration', 'level', 'content')

admin.site.register(Course, CourseAdmin)

# ShopItem admin (basic registration)
admin.site.register(ShopItem)

# PlayerProfile admin (basic registration)
admin.site.register(PlayerProfile)

# Purchase admin (optional customizations)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('player', 'item', 'purchased_at')
    list_filter = ('purchased_at',)
    search_fields = ('player__user__username', 'item__name')

admin.site.register(Purchase, PurchaseAdmin)

# Quiz admin
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text',)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course__level',)
    search_fields = ('title', 'course__title')
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)

# Question admin with options inline
class OptionInline(admin.TabularInline):
    model = Option
    extra = 3
    fields = ('text', 'is_correct')
    ordering = ('id',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'get_course')
    list_filter = ('quiz__course__level', 'quiz__course')
    search_fields = ('text', 'quiz__title', 'quiz__course__title')
    inlines = [OptionInline]
    
    def get_course(self, obj):
        return obj.quiz.course.title if obj.quiz and obj.quiz.course else "No Course"
    get_course.short_description = "Course"

admin.site.register(Question, QuestionAdmin)

# Option admin with better display
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'get_course')
    list_filter = ('is_correct', 'question__quiz__course')
    search_fields = ('text', 'question__text', 'question__quiz__title')
    list_editable = ('is_correct',)
    
    def get_course(self, obj):
        return obj.question.quiz.course.title if obj.question and obj.question.quiz and obj.question.quiz.course else "No Course"
    get_course.short_description = "Course"

admin.site.register(Option, OptionAdmin)
