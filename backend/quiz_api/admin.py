from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from .models import Student, Question, StudentAnswer, Leaderboard


# ── Custom form ───────────────────────────────────────────────────────────────

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        round_number = cleaned.get('round_number')

        if round_number == 1:
            for field in ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']:
                if not str(cleaned.get(field, '') or '').strip():
                    self.add_error(field, 'This field is required for Round 1 questions.')
            cleaned['difficulty']  = 'Medium'
            cleaned['examples']    = ''
            cleaned['constraints'] = ''
            cleaned['test_cases']  = []

        elif round_number == 2:
            for field in ['text', 'examples', 'constraints']:
                if not str(cleaned.get(field, '') or '').strip():
                    self.add_error(field, 'This field is required for Round 2 questions.')
            if not cleaned.get('test_cases'):
                self.add_error('test_cases', 'At least one test case is required for Round 2.')
            cleaned['option_a']       = ''
            cleaned['option_b']       = ''
            cleaned['option_c']       = ''
            cleaned['option_d']       = ''
            cleaned['correct_option'] = ''

        return cleaned


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm

    list_display  = ('id', 'text_preview', 'round_number_badge', 'points', 'difficulty')
    list_filter   = ('round_number', 'difficulty')
    ordering      = ('round_number', 'id')
    search_fields = ('text',)

    class Media:
        js  = ('admin/js/question_round_switch.js',)
        css = {'all': ('admin/css/question_admin.css',)}

    # ── Replace the default "ADD QUESTION" with two split buttons ─────────────
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        add_url = reverse('admin:quiz_api_question_add')
        extra_context['add_r1_url'] = f"{add_url}?round_number=1"
        extra_context['add_r2_url'] = f"{add_url}?round_number=2"
        return super().changelist_view(request, extra_context=extra_context)

    # Hide the default single "Add Question" button from the top-right
    def has_add_permission(self, request):
        return True  # keep permission, we just override the button via template

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            round_number = obj.round_number
        else:
            round_number = int(
                request.POST.get('round_number')
                or request.GET.get('round_number')
                or 1
            )

        if round_number == 2:
            return (
                ('Round 2 — Code Debugging', {
                    'fields': (
                        'round_number',
                        'points',
                        'difficulty',
                        'text',
                        'code_snippet',
                        'examples',
                        'constraints',
                        'test_cases',
                    ),
                    'description': (
                        'Fill in the problem statement, starter/buggy code, examples, '
                        'constraints, and test cases. '
                        'test_cases format: [{"input": "...", "expected_output": "..."}]'
                    ),
                }),
            )
        else:
            return (
                ('Round 1 — MCQ', {
                    'fields': (
                        'round_number',
                        'points',
                        'text',
                        'code_snippet',
                        'option_a',
                        'option_b',
                        'option_c',
                        'option_d',
                        'correct_option',
                    ),
                    'description': 'Fill in the question text, four answer options, and mark the correct one.',
                }),
            )

    def text_preview(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Question'

    def round_number_badge(self, obj):
        if obj.round_number == 1:
            return format_html(
                '<span class="round-badge round-badge--r1">Round 1 — MCQ</span>'
            )
        return format_html(
            '<span class="round-badge round-badge--r2">Round 2 — Debug</span>'
        )
    round_number_badge.short_description = 'Round'
    round_number_badge.admin_order_field = 'round_number'


# ── Other models (unchanged) ──────────────────────────────────────────────────

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display    = ('id', 'name', 'email', 'round1_score', 'round2_score',
                       'total_score', 'round1_completed', 'round2_qualified', 'round2_completed')
    ordering        = ('-total_score',)
    search_fields   = ('name', 'email')
    list_filter     = ('round1_completed', 'round2_qualified', 'round2_completed', 'current_round')
    readonly_fields = ('round1_score', 'round2_score', 'total_score')


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display    = ('id', 'name', 'email', 'round1_score', 'round2_score', 'total_score', 'round2_qualified')
    ordering        = ('-total_score',)
    readonly_fields = ('id', 'name', 'email', 'department', 'college', 'year',
                       'round1_score', 'round2_score', 'total_score',
                       'round1_completed', 'round2_qualified', 'round2_completed')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'chosen_option', 'is_correct', 'round_number')
    list_filter  = ('round_number', 'is_correct')