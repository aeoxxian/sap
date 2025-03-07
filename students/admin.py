from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    ClassGroup, Student, Exam, ExamResult, FieldDefinition, Parent,
    Assignment, AssignmentSubmission
)
from .forms import ExamResultForm, AssignmentSubmissionForm

# ---------------------------
# USER / PARENT
# ---------------------------

class ParentInline(admin.StackedInline):
    model = Parent
    can_delete = False
    verbose_name_plural = "학부모 정보"

class CustomUserAdmin(UserAdmin):
    inlines = [ParentInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')


# ---------------------------
# CLASSGROUP
# ---------------------------

class FieldDefinitionInline(admin.TabularInline):
    model = FieldDefinition
    extra = 1

class StudentInline(admin.TabularInline):
    model = Student
    extra = 0

class ExamInline(admin.TabularInline):
    model = Exam
    extra = 0

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [FieldDefinitionInline, StudentInline, ExamInline]


# ---------------------------
# STUDENT
# ---------------------------

class ExamResultInline(admin.TabularInline):
    model = ExamResult
    extra = 0

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'class_group')
    list_filter = ('class_group',)
    search_fields = ('name', 'school')
    inlines = [ExamResultInline]


# ---------------------------
# EXAM
# ---------------------------

class ExamResultInlineForExam(admin.TabularInline):
    model = ExamResult
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'class_group', 'date', 'average',
        'avg_field1', 'avg_field2', 'avg_field3', 'avg_field4', 'avg_field5',
        'top_scores'
    )
    list_filter = ('class_group', 'date')
    search_fields = ('name',)
    inlines = [ExamResultInlineForExam]


# ---------------------------
# EXAM RESULT
# ---------------------------

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    form = ExamResultForm
    list_display = (
        'student', 'exam', 'exam_date', 'total_score', 'max_score',
        'rank', 'status',
        'field1', 'field1_definition',
        'field2', 'field2_definition',
        'field3', 'field3_definition',
        'field4', 'field4_definition',
        'field5', 'field5_definition',
    )
    list_filter = ('status', 'exam')
    search_fields = ('student__name', 'exam__name')

    class Media:
        js = ("students/js/exam_result_admin.js",)


# ---------------------------
# ASSIGNMENT
# ---------------------------

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """
    하루에 최대 5개 과제명만 저장.
    => task1_name ~ task5_name
    """
    # title 필드가 없어졌으므로, list_display 수정
    list_display = ("class_group", "date", "task1_name", "task2_name", "task3_name", "task4_name", "task5_name")
    list_filter = ("class_group", "date")
    search_fields = ("task1_name", "task2_name", "task3_name", "task4_name", "task5_name")


# ---------------------------
# ASSIGNMENT SUBMISSION
# ---------------------------

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    """
    하루 과제 5개 각각에 대한 이행률(0~100)
    """
    form = AssignmentSubmissionForm

    # completion_rate라는 필드는 사라졌으므로,
    # completion_rate1~5로 변경
    list_display = (
        "assignment", "student",
        "completion_rate1", "completion_rate2",
        "completion_rate3", "completion_rate4",
        "completion_rate5"
    )
    list_filter = ("assignment__class_group", "assignment__date")
    search_fields = ("assignment__task1_name", "assignment__task2_name", 
                     "student__name")
