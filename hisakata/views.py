import datetime
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect

from . import models


def yearlist(request):
    years = range(models.startyear, models.nowyear + 1)
    return render(request, 'hisakata/yearlist.html', {
        'years': years
    })


def tableyearlist(request):
    years = range(models.startyear, models.nowyear + 1)
    return render(request, 'hisakata/tableyearlist.html', {
        'years': years
    })


class DateCreateView(generic.CreateView):
    model = models.Date
    form_class = models.DateForm
    template_name = "hisakata/dateform.html"


class DateListView(generic.ListView):
    model = models.Date
    template_name = "hisakata/datelist.html"


class MonthListView(generic.ListView):
    model = models.Date
    template_name = "hisakata/tablelist.html"


def detailview(request, year, month, day):
    date = get_object_or_404(models.Date, date=datetime.date(int(year), int(month), int(day)))
    new_game = date.round_set.count() + 1
    return render(request, 'hisakata/detail.html', {'date': date, 'new_game': new_game, })


def formview(request, year, month, day, round_n):
    date = datetime.date(int(year), int(month), int(day))
    round_num = models.Round.objects.get(round=round_n, class_date__date=date).round

    match = models.Match.objects.filter(round__round=round_n, round__class_date__date=date)
    formset = []

    if request.method == 'GET':
        for mt in match:
            li = [models.MatchForm(instance=mt), None, None]
            for playing in mt.playing_set.all():
                li[playing.player_num] = models.PlayerForm(instance=playing.player)
            formset.append(li)
        return render(request, 'hisakata/form.html', {'year': year,
                                                      'month': month,
                                                      'day': day,
                                                      'round_num': round_num,
                                                      'formset': formset, })

    else:
        names = request.POST.getlist('name')
        winners = request.POST.getlist('winner')
        results = request.POST.getlist('result')
        csrf = request.POST.get('csrfmiddlewaretoken')
        i_match = 0
        for mt in match:
            mform = models.MatchForm(
                {'winner': winners[i_match], 'result': results[i_match], 'csrfmiddlewaretoken': csrf}, instance=mt)
            i_match += 1
            if mform.is_valid():
                pform = [None, None]
                flag = True
                for playing in mt.playing_set.all():
                    p = models.PlayerForm({'name': names[i_match+playing.player_num-1], 'csrfmiddlewaretoken': csrf}, instance=playing.player)
                    pform[playing.player_num - 1] = p
                    if not p.is_valid():
                        flag = False
                if flag:
                    for pf in pform:
                        pf.save()
                    mform.save()

        return HttpResponseRedirect(match[0].get_absolute_url())


def createformview(request):
    return 0


def tableview(request, year, month):
    player = []
    flag = False

    for one in models.Player.objects.all():
        for match in one.match.all():
            if match.round.class_date.date.year == int(year) and match.round.class_date.date.month == int(month):
                flag = True
        if flag:
            player += [one]
        flag = False

    max_num = max([one.match.count() for one in player])

    return render(request, 'hisakata/table.html', {'year': year,
                                                   'month': month,
                                                   'player': player,
                                                   'max_num': range(max_num),
                                                   })
