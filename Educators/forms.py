from django import forms
from Quizzes.models import Quiz, Question, Option

class FullQuizForm(forms.Form):
    quiz_title = forms.CharField(label="Quiz Title", max_length=255)
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
