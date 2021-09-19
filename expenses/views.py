from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView, CreateView, DetailView
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm, CategorySearchForm
from .models import Expense, Category
from .reports import summary_per_category, summary_per_year_month, all_summary, count_expenses


class CategoryListView(ListView):
    #    6. Add list view for `expenses.Category`.
    #    7. Add number of expenses per category per row in `expenses.CategoryList`.
    model = Category
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        form = CategorySearchForm(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            if name:
                queryset = queryset.filter(name__icontains=name)
        return super().get_context_data(
            form=form,
            object_list=queryset,
            total_objects=queryset.count(),
            **kwargs
        )


class CategoryCreateView(SuccessMessageMixin, CreateView):
    #    10. Add message for create/update in `expenses.Category` if name already exists
    model = Category
    fields = ['name']
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:category-list')
    success_message = 'Successfully Created!'


class CategoryUpdateView(SuccessMessageMixin, UpdateView):
    #    10. Add message for create/update in `expenses.Category` if name already exists
    model = Category
    fields = ['name']
    success_url = reverse_lazy('expenses:category-list')
    success_message = 'Successfully Updated!'
    template_name = 'expenses/expense_form.html'


class CategoryDeleteView(SuccessMessageMixin, DeleteView):
    #   11. Add delete view for `expenses.Category`.
    #   12. In `expenses.CategoryDelete` add total count of expenses that will be deleted.
    model = Category
    success_url = reverse_lazy('expenses:category-list')
    template_name = 'expenses/expense_confirm_delete.html'
    success_message = 'Successfully Deleted!'

    def get_context_data(self, **kwargs):
        queryset = Expense.objects.filter(category=self.object)
        total_count = all_summary(queryset)

        return super().get_context_data(
            summary=total_count,
            count_expenses=count_expenses(self.get_object()),
            **kwargs
        )


class CategoryDetailView(DetailView):
    #    13. Add detail view for `expenses.Category` with total summary per year-month.
    model = Category
    template_name = 'expenses/category_detail.html'

    def get_context_data(self, **kwargs):
        queryset = Expense.objects.filter(category=self.object)

        return super().get_context_data(
            summary_per_year_month=summary_per_year_month(queryset),
            count_expenses=count_expenses(self.get_object()),
            **kwargs
        )


class ExpenseListView(ListView):
    #  1. Allow searching by date range in `expenses.ExpenseList`.
    #    2. Allow searching by multiple categories in `expenses.ExpenseList`.
    #    3. In `expenses.ExpenseList` add sorting by category and date (ascending and descending)
    #    4. In `expenses.ExpenseList` add grouping by category name (ascending and descending)
    #    5. In `expenses.ExpenseList` add total amount spent.
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        form = ExpenseSearchForm(self.request.GET)
        total_objects = queryset.count(),

        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            if name:
                queryset = queryset.filter(name__icontains=name)

            sort_date = form.cleaned_data['sort_date']
            if sort_date == "ascending":
                queryset = queryset.order_by('date')
            elif sort_date == "descending":
                queryset = queryset.order_by('-date')

            sort_category = form.cleaned_data['sort_category']
            if sort_category == "ascending":
                queryset = queryset.order_by('category')
            elif sort_category == "descending":
                queryset = queryset.order_by('-category')

            grouping = form.cleaned_data['grouping']
            if grouping == 'date':
                queryset = queryset.order_by('date', '-pk')
            elif grouping == 'category':
                queryset = queryset.order_by('category', '-pk')

            minimum_date = form.cleaned_data['minimum_date']
            maximum_date = form.cleaned_data['maximum_date']
            if minimum_date and maximum_date:
                queryset = queryset.filter(date__range=[minimum_date, maximum_date])

            categories = form.cleaned_data['categories']
            if categories:
                categories_list = [Category.objects.get(name=category) for category in categories]
                queryset = Expense.objects.filter(category__in=categories_list)

        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            summary_per_year_month=summary_per_year_month(queryset),
            overall_summary=all_summary(queryset),
            total_objects=total_objects,
            **kwargs)
