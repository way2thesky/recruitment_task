from django import forms
from .models import Expense, Category


class ExpenseSearchForm(forms.ModelForm):
    GROUPING = ('date',)
    SORTING = ('ascending', 'descending')

    grouping = forms.ChoiceField(choices=[('', '')] + list(zip(GROUPING, GROUPING)))
    sort_date = forms.ChoiceField(choices=[('', '')] + list(zip(SORTING, SORTING)))
    sort_category = forms.ChoiceField(choices=[('', '')] + list(zip(SORTING, SORTING)))

    categories = forms.ModelMultipleChoiceField(label='Category', widget=forms.CheckboxSelectMultiple,
                                                queryset=Category.objects.all())
    minimum_date = forms.DateTimeField(required=True,
                                       widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM'}))
    maximum_date = forms.DateTimeField(required=True,
                                       widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM'}))

    class Meta:
        model = Expense
        fields = ('name', 'category',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].required = False


class CategorySearchForm(forms.Form):
    name = forms.CharField(max_length=75)

    class Meta:
        model = Category
        exclude = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].required = False
