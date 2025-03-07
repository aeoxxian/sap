from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import ExamResult, FieldDefinition, Student, Parent
from .models import AssignmentSubmission, Assignment

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV 파일 업로드")

class ParentLoginForm(AuthenticationForm):
    username = forms.CharField(label="아이디", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # 이미 존재하는 ExamResult 수정 시
            student = self.instance.student
            class_group = student.class_group
            self.fields["field1_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field2_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field3_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field4_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field5_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
        else:
            # 새로 ExamResult를 생성할 때는 분반 정보가 없으므로 빈 쿼리셋
            self.fields["field1_definition"].queryset = FieldDefinition.objects.none()
            self.fields["field2_definition"].queryset = FieldDefinition.objects.none()
            self.fields["field3_definition"].queryset = FieldDefinition.objects.none()
            self.fields["field4_definition"].queryset = FieldDefinition.objects.none()
            self.fields["field5_definition"].queryset = FieldDefinition.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        if student:
            class_group = student.class_group
            self.fields["field1_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field2_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field3_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field4_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
            self.fields["field5_definition"].queryset = FieldDefinition.objects.filter(class_group=class_group)
        return cleaned_data

class ParentSignUpForm(UserCreationForm):
    """
    학부모 회원가입 폼 - ModelChoiceField로 기존 Student 선택.
    이름 (분반) 형태로 라벨 표시되도록 label_from_instance 오버라이딩.
    """
    email = forms.EmailField(required=True, label="이메일")

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="학생 선택",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="학생의 이름과 소속된 분반을 선택하세요."
    )

    password1 = forms.CharField(
        label="비밀번호",
        strip=False,
        widget=forms.PasswordInput,
        help_text="비밀번호는 8자 이상이어야 하며, 숫자로만 이루어질 수 없습니다.",
        error_messages={
            "required": "비밀번호를 입력해 주세요.",
            "min_length": "비밀번호는 최소 8자 이상이어야 합니다.",
            "password_mismatch": "비밀번호가 일치하지 않습니다.",
            "common_password": "너무 흔히 사용되는 비밀번호입니다.",
            "numeric_password": "비밀번호는 숫자로만 이루어질 수 없습니다.",
        },
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput,
        strip=False,
        help_text="위에서 입력한 비밀번호와 동일하게 입력해 주세요.",
        error_messages={
            "required": "비밀번호 확인을 입력해 주세요.",
            "password_mismatch": "비밀번호가 일치하지 않습니다.",
        },
    )

    class Meta:
        model = User
        fields = ("username", "email", "student", "password1", "password2")
        labels = {
            "username": "아이디",
        }
        help_texts = {
            "username": "영문자, 숫자, @/./+/-/_ 만 사용 가능합니다.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # student field에서 학생 이름 (분반) 형태로 표시되도록 설정
        self.fields["student"].label_from_instance = (
            lambda obj: f"{obj.name} ({obj.class_group.name})"
        )


            
            
class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = "__all__"  # assignment, student, completion_rate

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # (1) 이미 pk가 있는 경우(기존 레코드 수정) => instance.assignment가 존재
        if self.instance.pk:
            assignment_obj = self.instance.assignment
            if assignment_obj:
                # 과제가 선택된 상태이므로, 분반(class_group)에 속한 학생만 필터링
                self.fields["student"].queryset = Student.objects.filter(
                    class_group=assignment_obj.class_group
                )
        else:
            # (2) 새로 레코드를 생성하는 경우 => pk 없음
            #     django admin에서 과제를 선택하지 않은 상태일 수도 있음
            self.fields["student"].queryset = Student.objects.none()

            # 만약 Admin 폼이 "POST"로 한번 제출되었지만, 아직 DB에 저장 전(유효성 검증 실패) => self.data 사용
            if "assignment" in self.data:
                try:
                    assignment_id = int(self.data.get("assignment"))
                    assignment_obj = Assignment.objects.get(id=assignment_id)
                    self.fields["student"].queryset = Student.objects.filter(
                        class_group=assignment_obj.class_group
                    )
                except (ValueError, Assignment.DoesNotExist):
                    self.fields["student"].queryset = Student.objects.none()