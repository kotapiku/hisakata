import datetime
from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.http import HttpResponseRedirect

from . import models
from django.template.defaulttags import register


@register.filter
def get_item(list, num):
    return list[num]


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


def datelistview(request, year):
    dates = models.Date.objects.filter(date__year=year)
    youbi = ['月', '火', '水', '木', '金', '土', '日']
    return render(request, 'hisakata/datelist.html', {'dates': dates, 'year': year, 'youbi': youbi})


def datecreateview(request, year):
    if request.method == 'GET':
        return render(request, 'hisakata/dateform.html', {'year': year})
    else:
        error_message = ''
        date = datetime.date(int(request.POST['date'][:4]), int(request.POST['date'][5:7]),
                             int(request.POST['date'][8:]))

        if models.Date.objects.filter(date=date).count() != 0:
            error_message = '重複する日付は入力できません'
        if datetime.date.today() < date:
            error_message = '未来の日付は入力できません'

        if error_message:
            return render(request, 'hisakata/dateform.html', {'year': year, 'error_message': error_message})
        else:
            form = models.DateForm(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(reverse("hisakata:datelist", kwargs={'year': year}))


class MonthListView(generic.ListView):
    model = models.Date
    template_name = "hisakata/tablelist.html"


def detailview(request, year, month, day):
    date = get_object_or_404(models.Date, date=datetime.date(int(year), int(month), int(day)))
    new_game = date.round_set.last().round + 1
    return render(request, 'hisakata/detail.html', {'date': date, 'new_game': new_game, })


def formview(request, year, month, day, round_n):
    date = datetime.date(int(year), int(month), int(day))

    formset = []

    if request.method == 'GET':
        round = models.Round.objects.filter(round=round_n, class_date__date=date)
        extra = 5
        if round.count() == 0:  # 新規
            models.Round.objects.create(round=round_n, class_date=models.Date.objects.get(date=date))
            round = models.Round.objects.get(round=round_n, class_date__date=date)
            roundform = models.RoundForm(instance=round)
            comment = round.comment
            for i in range(extra):
                models.Match.objects.create(round=models.Round.objects.get(round=round_n, class_date__date=date))
            for match in models.Match.objects.filter(round__round=round_n, round__class_date__date=date):
                formset.append([models.MatchForm(instance=match), "", ""])

            return render(request, 'hisakata/form.html', {'year': year,
                                                          'month': month,
                                                          'day': day,
                                                          'round_num': round_n,
                                                          'roundform': roundform,
                                                          'comment': comment,
                                                          'formset': formset, })
        else:  # 既存
            round = round[0]
            match = models.Match.objects.filter(round__round=round_n, round__class_date__date=date)
            roundform = models.RoundForm(instance=round)
            comment = round.comment
            for mt in match:
                li = [models.MatchForm(instance=mt), "", ""]
                for playing in mt.playing_set.all():
                    li[playing.player_num] = playing.player.name
                formset.append(li)
            return render(request, 'hisakata/form.html', {'year': year,
                                                          'month': month,
                                                          'day': day,
                                                          'round_num': round_n,
                                                          'roundform': roundform,
                                                          'comment': comment,
                                                          'formset': formset, })

    # request.method == 'POST'
    else:
        names = request.POST.getlist('name')
        winners = request.POST.getlist('winner')
        results = request.POST.getlist('result')
        comment = request.POST['comment']
        round_num = request.POST['round']
        csrf = request.POST.get('csrfmiddlewaretoken')

        if models.Round.objects.filter(round=round_num, class_date__date=date).count() > 1:
            error_message = "適切な試合番号を入力してください。"
            round_model = models.Round.objects.get(round=round_n, class_date__date=date)
            match = models.Match.objects.filter(round__round=round_n, round__class_date__date=date)
            roundform = models.RoundForm(instance=round_model)
            for mt in match:
                li = [models.MatchForm(instance=mt), "", ""]
                for playing in mt.playing_set.all():
                    li[playing.player_num] = playing.player.name
                formset.append(li)
            return render(request, 'hisakata/form.html', {'year': year,
                                                          'month': month,
                                                          'day': day,
                                                          'error_message': error_message,
                                                          'round_num': round_n,
                                                          'roundform': roundform,
                                                          'formset': formset, })


        else:
            if models.Round.objects.filter(round=round_num, class_date__date=date).count() == 0:
                models.Round.objects.create(round=round_num, class_date=models.Date.objects.get(date=date))
                for i in range(len(winners)):
                    models.Match.objects.create(round=models.Round.objects.get(round=round_num, class_date__date=date))
                models.Round.objects.filter(round=round_n, class_date__date=date).delete()
                for match in models.Match.objects.filter(round__round=round_n, round__class_date__date=date):
                    match.playing_set.delete()
                models.Match.objects.filter(round__round=round_n, round__class_date__date=date).delete()

            i_match = 0

            round_model = models.Round.objects.get(round=round_num, class_date__date=date)
            roundform = models.RoundForm({'round': round_num, 'comment': comment, 'csrfmiddlewaretoken': csrf},
                                         instance=round_model)
            match = models.Match.objects.filter(round__round=round_num, round__class_date__date=date)
            if roundform.is_valid():
                for mt in match:
                    mform = models.MatchForm(
                        {'winner': winners[i_match], 'result': results[i_match], 'csrfmiddlewaretoken': csrf},
                        instance=mt)
                    if not names[2 * i_match] or not names[2 * i_match + 1]:
                        mt.delete()
                    else:
                        if mform.is_valid():
                            if mt.playing_set.count() != 0:  # 既存の試合の場合
                                for playing in mt.playing_set.all():
                                    player = models.Player.objects.get(name=names[2 * i_match + playing.player_num - 1])
                                    playing.player = player

                                    playing.save()
                            else:  # 新規の試合の場合
                                player1 = models.Player.objects.get(name=names[2 * i_match])
                                models.Playing.objects.create(player=player1, match=mt, player_num=1)
                                player2 = models.Player.objects.get(name=names[2 * i_match + 1])
                                models.Playing.objects.create(player=player2, match=mt, player_num=2)

                            mform.save()
                            roundform.save()

                    i_match += 1

            if models.Match.objects.filter(round__round=round_num, round__class_date__date=date).count() == 0:
                models.Round.objects.get(round=round_num, class_date__date=date).delete()

            return HttpResponseRedirect(reverse("hisakata:detail", kwargs={'year': year,
                                                                           'month': month,
                                                                           'day': day}))


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
