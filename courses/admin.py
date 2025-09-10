# courses/admin.py
from django.contrib import admin
from .models import Course, ShopItem, PlayerProfile, Purchase, Quiz, Question, Option

# Course admin with custom display
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'duration')
    fields = ('title', 'description', 'duration', 'category', 'level', 'content')

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

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title',)
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)

# Question admin with options inline
class OptionInline(admin.TabularInline):
    model = Option
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    inlines = [OptionInline]

admin.site.register(Question, QuestionAdmin)

# Option admin (basic registration)
admin.site.register(Option)
