from django.db import migrations


ROUND2_QUESTION = {
    "text": "This Python function is supposed to count vowels in a string, but it misses uppercase vowels. What should be fixed?",
    "code_snippet": "def count_vowels(text):\n    vowels = 'aeiou'\n    count = 0\n    for ch in text:\n        if ch in vowels:\n            count += 1\n    return count\n\nprint(count_vowels('OpenAI'))",
    "option_a": "Replace the for loop with while",
    "option_b": "Convert text to lowercase before checking vowels",
    "option_c": "Change count += 1 to count = 1",
    "option_d": "Use a list instead of a string for vowels",
    "correct_option": "B",
    "points": 10,
}


def add_round2_question(apps, schema_editor):
    Question = apps.get_model('quiz_api', 'Question')
    Question.objects.get_or_create(
        text=ROUND2_QUESTION["text"],
        defaults={
            "code_snippet": ROUND2_QUESTION["code_snippet"],
            "option_a": ROUND2_QUESTION["option_a"],
            "option_b": ROUND2_QUESTION["option_b"],
            "option_c": ROUND2_QUESTION["option_c"],
            "option_d": ROUND2_QUESTION["option_d"],
            "correct_option": ROUND2_QUESTION["correct_option"],
            "round_number": 2,
            "points": ROUND2_QUESTION["points"],
        }
    )


def remove_round2_question(apps, schema_editor):
    Question = apps.get_model('quiz_api', 'Question')
    Question.objects.filter(text=ROUND2_QUESTION["text"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_api', '0007_studentanswer_submitted_code_and_more'),
    ]

    operations = [
        migrations.RunPython(add_round2_question, remove_round2_question),
    ]
