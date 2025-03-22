from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# -----------------------------
# 분반 (ClassGroup)
# -----------------------------
class ClassGroup(models.Model):
    name = models.CharField("분반 이름", max_length=50)

    class Meta:
        verbose_name = "분반"
        verbose_name_plural = "분반들"

    def __str__(self):
        return self.name


# -----------------------------
# 학부모 (Parent)
# -----------------------------
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="학부모 계정")
    phone_number = models.CharField("전화번호", max_length=20, null=True, blank=True)
    # ManyToManyField는 학생 쪽(Student)에서 정의되어 있음 (parents = ...)

    class Meta:
        verbose_name = "학부모"
        verbose_name_plural = "학부모들"

    def __str__(self):
        return self.user.username


# -----------------------------
# 학생 (Student)
# -----------------------------
class Student(models.Model):
    name = models.CharField("학생 이름", max_length=50)
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name="분반"
    )
    school = models.CharField("출신 학교", max_length=100)

    # ✅ 학부모 ↔ 학생 M2M 필드를 Student 쪽에 정의
    parents = models.ManyToManyField(
        Parent,
        related_name="children",  # Parent에서 역참조 시 parent.children.all()
        blank=True,
        verbose_name="학부모 목록"
    )

    class Meta:
        verbose_name = "학생"
        verbose_name_plural = "학생들"

    def __str__(self):
        return f"{self.name} ({self.class_group.name})"


@receiver(post_save, sender=User)
def create_parent_profile(sender, instance, created, **kwargs):
    """
    새 User가 생성되면 Parent를 자동 생성 (학부모 계정용)
    """
    if created:
        Parent.objects.create(user=instance)


# -----------------------------
# 시험 (Exam)
# -----------------------------
class Exam(models.Model):
    name = models.CharField("시험 이름", max_length=100)
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name="시험 실시 분반"
    )
    date = models.DateField("시험 실시 날짜", null=True, blank=True)
    average = models.FloatField("시험 평균", null=True, blank=True)
    top_scores = models.CharField("상위 점수 3개", max_length=200, null=True, blank=True)

    avg_field1 = models.FloatField("분야1 평균", null=True, blank=True, default=0)
    avg_field2 = models.FloatField("분야2 평균", null=True, blank=True, default=0)
    avg_field3 = models.FloatField("분야3 평균", null=True, blank=True, default=0)
    avg_field4 = models.FloatField("분야4 평균", null=True, blank=True, default=0)
    avg_field5 = models.FloatField("분야5 평균", null=True, blank=True, default=0)

    class Meta:
        verbose_name = "시험"
        verbose_name_plural = "시험들"

    def __str__(self):
        return f"{self.name} ({self.class_group.name})"

    def update_field_averages(self):
        from django.db.models import Avg
        results = self.exam_results.all()

        agg = results.aggregate(
            avg1=Avg('field1'),
            avg2=Avg('field2'),
            avg3=Avg('field3'),
            avg4=Avg('field4'),
            avg5=Avg('field5'),
        )
        self.avg_field1 = round(agg['avg1'], 2) if agg['avg1'] else 0
        self.avg_field2 = round(agg['avg2'], 2) if agg['avg2'] else 0
        self.avg_field3 = round(agg['avg3'], 2) if agg['avg3'] else 0
        self.avg_field4 = round(agg['avg4'], 2) if agg['avg4'] else 0
        self.avg_field5 = round(agg['avg5'], 2) if agg['avg5'] else 0
        self.save(update_fields=[
            'avg_field1','avg_field2','avg_field3','avg_field4','avg_field5'
        ])


# -----------------------------
# 분야 정의 (FieldDefinition)
# -----------------------------
class FieldDefinition(models.Model):
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name='field_definitions',
        verbose_name="분반"
    )
    name = models.CharField("분야 이름", max_length=50)

    class Meta:
        verbose_name = "시험 분야"
        verbose_name_plural = "시험 분야들"

    def __str__(self):
        return f"{self.class_group.name} - {self.name}"


# -----------------------------
# 시험 결과 (ExamResult)
# -----------------------------
class ExamResult(models.Model):
    STATUS_CHOICES = (
        ('응시', '응시'),
        ('결석', '결석'),
        ('녹화본', '녹화본'),
        ('조퇴', '조퇴'),
        ('라이브', '라이브'),
        ('미응시', '미응시'),
        ('내신', '내신'),
    )

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='exam_results', verbose_name="학생"
    )
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE,
        related_name='exam_results', verbose_name="시험"
    )
    exam_date = models.DateField("시험 실시 날짜", null=True, blank=True)
    status = models.CharField("응시 상태", max_length=10, choices=STATUS_CHOICES)
    total_score = models.FloatField("총점", null=True, blank=True, default=0)
    max_score = models.FloatField("만점", null=True, blank=True, default=100)
    rank = models.IntegerField("석차", null=True, blank=True, default=-1)

    field1 = models.FloatField("분야별 점수 - Field1", null=True, blank=True, default=0)
    field2 = models.FloatField("분야별 점수 - Field2", null=True, blank=True, default=0)
    field3 = models.FloatField("분야별 점수 - Field3", null=True, blank=True, default=0)
    field4 = models.FloatField("분야별 점수 - Field4", null=True, blank=True, default=0)
    field5 = models.FloatField("분야별 점수 - Field5", null=True, blank=True, default=0)

    field1_definition = models.ForeignKey(
        FieldDefinition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exam_results_field1",
        verbose_name="분야1 이름"
    )
    field2_definition = models.ForeignKey(
        FieldDefinition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exam_results_field2",
        verbose_name="분야2 이름"
    )
    field3_definition = models.ForeignKey(
        FieldDefinition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exam_results_field3",
        verbose_name="분야3 이름"
    )
    field4_definition = models.ForeignKey(
        FieldDefinition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exam_results_field4",
        verbose_name="분야4 이름"
    )
    field5_definition = models.ForeignKey(
        FieldDefinition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exam_results_field5",
        verbose_name="분야5 이름"
    )

    class Meta:
        verbose_name = "시험 결과"
        verbose_name_plural = "시험 결과들"

    def __str__(self):
        return f"{self.student.name} - {self.exam.name} ({self.status})"


@receiver(post_save, sender=ExamResult)
def update_exam_field_averages_on_save(sender, instance, **kwargs):
    exam = instance.exam
    exam.update_field_averages()


@receiver(post_delete, sender=ExamResult)
def update_exam_field_averages_on_delete(sender, instance, **kwargs):
    exam = instance.exam
    exam.update_field_averages()


# ============================
# ========== 과제(Assignment) 및 학생별 이행률(AssignmentSubmission)
# ============================
class Assignment(models.Model):
    class_group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE,
        related_name="assignments", verbose_name="분반"
    )
    date = models.DateField("날짜")

    task1_name = models.CharField("과제1 이름", max_length=200, blank=True)
    task2_name = models.CharField("과제2 이름", max_length=200, blank=True)
    task3_name = models.CharField("과제3 이름", max_length=200, blank=True)
    task4_name = models.CharField("과제4 이름", max_length=200, blank=True)
    task5_name = models.CharField("과제5 이름", max_length=200, blank=True)

    class Meta:
        verbose_name = "과제"
        verbose_name_plural = "과제 목록"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.class_group.name} ({self.date})"


class AssignmentSubmission(models.Model):
    """
    하루의 과제(Assignment)에 대해 최대 5개의 과제 각각의 이행률을 저장
    """
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE,
        related_name="submissions", verbose_name="과제"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name="assignment_submissions", verbose_name="학생"
    )

    # 각 과제별 이행률 (0~100)
    completion_rate1 = models.FloatField("과제1 이행률", default=0.0)
    completion_rate2 = models.FloatField("과제2 이행률", default=0.0)
    completion_rate3 = models.FloatField("과제3 이행률", default=0.0)
    completion_rate4 = models.FloatField("과제4 이행률", default=0.0)
    completion_rate5 = models.FloatField("과제5 이행률", default=0.0)

    daily_comment = models.TextField("일일 코멘트", blank=True)

    class Meta:
        verbose_name = "과제 이행 정보"
        verbose_name_plural = "과제 이행 정보들"
        unique_together = ("assignment", "student")

    def __str__(self):
        return f"{self.assignment} - {self.student.name}"