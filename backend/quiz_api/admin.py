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
                ('Round 2 — Language-Specific Snippets', {
                    'fields': (
                        'round_number',
                        'points',
                        'difficulty',
                        'text',
                        'code_python',
                        'test_cases_python',
                        'code_java',
                        'test_cases_java',
                        'code_c',
                        'test_cases_c',
                        'examples',
                        'constraints',
                        'test_cases',
                    ),
                    'description': (
                        'Enter the problem statement, snippets, and optionally, language-specific test cases. '
                        'Test cases use JSON format: [{"input": "5", "expected_output": "120"}]. '
                        'Keys "input", "stdin", "in" are accepted for input; "expected_output", "expected", "output" for output.'
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
                        'code_python',
                        'option_a',
                        'option_b',
                        'option_c',
                        'option_d',
                        'correct_option',
                    ),
                    'description': 'Fill in the question text, code (if any), options, and mark the correct one.',
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
    list_display    = ('rank', 'name', 'email', 'college', 'round1_score', 'round2_score', 'total_score', 'round2_qualified')
    ordering        = ('-total_score', '-round2_score', 'id')
    readonly_fields = ('id', 'name', 'email', 'department', 'college', 'year',
                       'round1_score', 'round2_score', 'total_score',
                       'round1_completed', 'round2_qualified', 'round2_completed')
    search_fields   = ('name', 'email', 'college')
    list_filter     = ('round2_qualified', 'round2_completed')
    list_per_page   = 50

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def rank(self, obj):
        # Rank is computed from position in the ordered queryset
        qs = Leaderboard.objects.order_by('-total_score', '-round2_score', 'id')
        ids = list(qs.values_list('id', flat=True))
        try:
            position = ids.index(obj.id) + 1
        except ValueError:
            return '-'
        if position == 1:
            return format_html('<strong style="color:#f59e0b;font-size:1.2em">🥇 1</strong>')
        if position == 2:
            return format_html('<strong style="color:#94a3b8;font-size:1.1em">🥈 2</strong>')
        if position == 3:
            return format_html('<strong style="color:#b45309;font-size:1.1em">🥉 3</strong>')
        return format_html('<span style="color:#64748b;font-weight:600">#{}</span>', position)
    rank.short_description = 'Rank'
    rank.admin_order_field = None  # Computed, not DB-sortable directly


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'chosen_option', 'is_correct', 'round_number')
    list_filter  = ('round_number', 'is_correct')