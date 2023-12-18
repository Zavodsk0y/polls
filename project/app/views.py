from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView

from .forms import *
from .models import *


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class BBLoginView(LoginView):
    template_name = 'main/login.html'
    success_url = '/accounts/profile/'


@login_required
def profile(request):
    return render(request, 'main/profile.html')


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin,
                         UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('app:index')
    success_message = 'Личные данные пользователя изменены'


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin,
                           PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('app:profile')
    success_message = 'Пароль пользователя изменен'


class SignUpView(CreateView):
    template_name = 'main/signup.html'
    success_url = reverse_lazy('app:profile')
    form_class = SignUpForm


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('app:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class Index(ListView):
    model = Poll
    template_name = 'main/index.html'
    context_object_name = 'polls'

    def get_queryset(self):
        return Poll.objects.filter(end_date__gte=timezone.now())


class DetailPoll(DetailView):
    model = Poll
    template_name = 'main/detail.html'
    context_object_name = 'polls'


class ResultsView(DetailView):
    model = Poll
    template_name = 'main/results.html'
    context_object_name = 'polls'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        poll = self.object
        total_votes = poll.choice_set.aggregate(total_votes=Sum('votes'))['total_votes']

        choices_with_percentages = []
        for choice in poll.choice_set.all():
            percentage = (choice.votes / total_votes) * 100 if total_votes > 0 else 0
            choices_with_percentages.append((choice, percentage))

        context['choices_with_percentages'] = choices_with_percentages
        return context


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if Voter.objects.filter(poll_id=poll_id, user_id=request.user.id).exists():
        messages.error(request, "Вы уже голосовали в этом опросе.")
        return HttpResponseRedirect(reverse('app:index'))
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'main/detail.html', {
            'poll': poll,
            'error_message': "Вы ничего не выбрали",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        v = Voter(user=request.user, poll=poll)
        v.save()
        return HttpResponseRedirect(reverse('app:results', args=(poll.id,)))
