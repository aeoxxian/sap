import io, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
import json
import tempfile
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from .forms import CSVUploadForm, ParentLoginForm, ParentSignUpForm, AssignmentSubmissionForm
from .models import (
    ClassGroup, Student, Exam, ExamResult, Parent, FieldDefinition,
    Assignment, AssignmentSubmission
)


def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            data = csv_file.read().decode('utf-8-sig')
            df = pd.read_csv(io.StringIO(data))
            for index, row in df.iterrows():
                try:
                    class_group_obj, _ = ClassGroup.objects.get_or_create(name=row["분반"])
                    student_obj, _ = Student.objects.get_or_create(
                        name=row["학생 이름"],
                        class_group=class_group_obj,
                        defaults={'school': ''}
                    )
                    exam_obj, _ = Exam.objects.get_or_create(
                        name=row["시험 이름"],
                        class_group=class_group_obj,
                        date=row["시험 실시 날짜"],
                        defaults={
                            'average': row["평균"] if pd.notna(row["평균"]) else 0,
                            'top_scores': row["상위 점수 3개"] if pd.notna(row["상위 점수 3개"]) else "",
                        }
                    )
                    max_score = 100
                    total_score = row["총점"] if pd.notna(row["총점"]) else 0
                    rank_value = row["석차"]
                    rank = None if pd.isna(rank_value) or (isinstance(rank_value, str) and not rank_value.isdigit()) else int(rank_value)
                    status = row["응시 상태"]

                    ExamResult.objects.create(
                        student=student_obj,
                        exam=exam_obj,
                        exam_date=row["시험 실시 날짜"],
                        status=status,
                        total_score=total_score,
                        max_score=max_score,
                        rank=rank,
                        field1=row["분야1"] if pd.notna(row["분야1"]) else None,
                        field2=row["분야2"] if pd.notna(row["분야2"]) else None,
                        field3=row["분야3"] if pd.notna(row["분야3"]) else None,
                        field4=row["분야4"] if pd.notna(row["분야4"]) else None,
                        field5=row["분야5"] if pd.notna(row["분야5"]) else None,
                    )
                except Exception as e:
                    print(f"Error processing row {index}: {e}")
                    continue

            messages.success(request, "CSV 파일 업로드 및 데이터 저장이 완료되었습니다.")
            return redirect('csv_upload')
    else:
        form = CSVUploadForm()
    return render(request, 'students/upload.html', {'form': form})


def parent_login(request):
    if request.method == "POST":
        form = ParentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("parent_dashboard")
        else:
            messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
    else:
        form = ParentLoginForm()
    return render(request, "students/parent_login.html", {"form": form})


def parent_logout(request):
    logout(request)
    return redirect("parent_login")


def parent_signup(request):
    """
    학부모 회원가입 - 기존 등록된 학생을 선택하여 학부모 계정과 연결
    """
    if request.method == "POST":
        form = ParentSignUpForm(request.POST)
        if form.is_valid():
            # 새로운 User 계정 생성
            user = form.save()
            # student: ModelChoiceField => Student 객체
            chosen_student = form.cleaned_data["student"]
            # 학부모 계정과 학생 연결
            parent = user.parent
            parent.students.add(chosen_student)
            # 회원가입 후 자동 로그인
            login(request, user)
            return redirect("parent_dashboard")
        else:
            messages.error(request, "회원가입 정보가 올바르지 않습니다.")
    else:
        form = ParentSignUpForm()
    
    return render(request, "students/parent_signup.html", {"form": form})


@login_required
def parent_dashboard(request):
    """
    대시보드:
    1) 가장 최근 과제 + 코멘트 + 이행률 표시
    2) 그 아래에 '모든 시험 보기', '모든 과제 보기' 링크
    3) 2개 시험 그래프(최근10, 전체) => 기존 parent_dashboard.html에서 처리
    """
    try:
        parent = Parent.objects.get(user=request.user)
        student = parent.students.first()
        if not student:
            return render(request, 'students/parent_dashboard.html', {'error': "배정된 학생이 없습니다."})

        # 가장 최근 과제
        latest_assignment = Assignment.objects.filter(class_group=student.class_group).order_by('-date').first()
        latest_submission = None
        if latest_assignment:
            # 학생이 제출한 이행률(AssignmentSubmission)
            latest_submission = AssignmentSubmission.objects.filter(
                assignment=latest_assignment,
                student=student
            ).first()

        return render(request, "students/parent_dashboard.html", {
            "student": student,
            "latest_assignment": latest_assignment,
            "latest_submission": latest_submission,
        })
    except Parent.DoesNotExist:
        messages.error(request, "해당 계정은 학부모 계정이 아닙니다.")
        return redirect("parent_login")


@login_required
def all_exams_view(request, student_id):
    """
    모든 시험 목록 표를 새 탭에서 보여주는 뷰
    """
    parent = request.user.parent
    student = get_object_or_404(Student, id=student_id)
    if not parent.students.filter(id=student_id).exists():
        messages.error(request, "접근 권한이 없습니다.")
        return redirect("parent_dashboard")

    exam_results = ExamResult.objects.filter(student=student).order_by('-exam__date')
    return render(request, "students/all_exams.html", {
        "student": student,
        "exam_results": exam_results,
    })


@login_required
def all_assignments_view(request, student_id):
    """
    모든 과제 보기 - 날짜별 과제명5개, 이행률5개, 학생별 코멘트(AssignmentSubmission.daily_comment).
    """
    parent = request.user.parent
    student = get_object_or_404(Student, id=student_id)
    if not parent.students.filter(id=student.id).exists():
        messages.error(request, "접근 권한이 없습니다.")
        return redirect("parent_dashboard")

    class_group = student.class_group
    assignments = Assignment.objects.filter(class_group=class_group).order_by("-date")

    # submission_dict: { assignment_id: submission_obj }
    from .models import AssignmentSubmission
    submission_dict = {}
    subs = AssignmentSubmission.objects.filter(student=student, assignment__in=assignments)
    for s in subs:
        submission_dict[s.assignment_id] = s
    
    # 각 assignment에 a.submission 연결
    for a in assignments:
        a.submission = submission_dict.get(a.id, None)

    return render(request, "students/all_assignments.html", {
        "student": student,
        "assignments": assignments,
    })




@login_required
def exam_detail(request, student_id, exam_id):
    exam_result = get_object_or_404(ExamResult, student__id=student_id, exam__id=exam_id)
    return render(request, "students/exam_detail.html", {
        "exam_result": exam_result
    })


@login_required
def exam_chart_data(request):
    """
    학생의 최근 10회 시험 성적과 반 평균 데이터를 JSON 형식으로 반환
    """
    try:
        parent = Parent.objects.get(user=request.user)
        student = parent.students.first()
        if not student:
            return JsonResponse({"error": "배정된 학생이 없습니다."}, status=400)

        results = ExamResult.objects.filter(student=student).order_by('-exam__date')[:10]
        results = list(results)[::-1]
        data = {
            "exam_names": [r.exam.name for r in results],
            "student_scores": [r.total_score for r in results],
            "class_averages": [r.exam.average for r in results],
        }
        return JsonResponse(data)
    except (Parent.DoesNotExist, AttributeError):
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)


@login_required
def exam_chart_all_data(request):
    """
    학생의 전체 시험 성적과 반 평균 데이터를 JSON 형식으로 반환
    """
    try:
        parent = Parent.objects.get(user=request.user)
        student = parent.students.first()
        if not student:
            return JsonResponse({"error": "배정된 학생이 없습니다."}, status=400)

        results = ExamResult.objects.filter(student=student).order_by('exam__date')
        data = {
            "exam_names": [r.exam.name for r in results],
            "student_scores": [r.total_score for r in results],
            "class_averages": [r.exam.average for r in results],
        }
        return JsonResponse(data)
    except (Parent.DoesNotExist, AttributeError):
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)


@login_required
def download_exam_pdf(request, exam_id):
    exam_result = get_object_or_404(ExamResult, id=exam_id)
    # 분야별 학생 점수 & 반 평균
    field_data = [
        {
            "label": "분야1",
            "score": exam_result.field1,
            "avg_score": exam_result.exam.avg_field1,
            "definition": exam_result.field1_definition.name if exam_result.field1_definition else "",
        },
        {
            "label": "분야2",
            "score": exam_result.field2,
            "avg_score": exam_result.exam.avg_field2,
            "definition": exam_result.field2_definition.name if exam_result.field2_definition else "",
        },
        {
            "label": "분야3",
            "score": exam_result.field3,
            "avg_score": exam_result.exam.avg_field3,
            "definition": exam_result.field3_definition.name if exam_result.field3_definition else "",
        },
        {
            "label": "분야4",
            "score": exam_result.field4,
            "avg_score": exam_result.exam.avg_field4,
            "definition": exam_result.field4_definition.name if exam_result.field4_definition else "",
        },
        {
            "label": "분야5",
            "score": exam_result.field5,
            "avg_score": exam_result.exam.avg_field5,
            "definition": exam_result.field5_definition.name if exam_result.field5_definition else "",
        },
    ]

    context = {
        "exam_result": exam_result,
        "field_data": field_data,
    }

    html_string = render_to_string("students/exam_pdf_template.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"{exam_result.exam.name}_성적.pdf\"'

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_filename = tmp_file.name
    try:
        HTML(string=html_string).write_pdf(tmp_filename)
        with open(tmp_filename, 'rb') as f:
            response.write(f.read())
    finally:
        os.remove(tmp_filename)

    return response


def get_field_definitions(request):
    """
    특정 Student 객체를 기반으로 FieldDefinition 목록을 필터링해 반환
    """
    student_id = request.GET.get("student_id")
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            class_group = student.class_group
            field_defs = FieldDefinition.objects.filter(class_group=class_group)
            data = [{"id": f.id, "name": f.name} for f in field_defs]
            return JsonResponse({"fields": data}, safe=False)
        except Student.DoesNotExist:
            return JsonResponse({"error": "해당 학생을 찾을 수 없습니다."}, status=400)
    return JsonResponse({"error": "잘못된 요청"}, status=400)
