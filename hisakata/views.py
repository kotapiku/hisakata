import datetime
from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.http import HttpResponseRedirect

from . import models
from django.template.defaulttags import register

youbi = ['月', '火', '水', '木', '金', '土', '日']


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
    caution = []
    for date in dates:
        if date.round_set.count() == 0:
            caution.append(False)
        else:
            caution.append(True)
    return render(request, 'hisakata/datelist.html',
                  {'dates': dates, 'year': year, 'youbi': youbi, 'caution': caution, })


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
    date_num = datetime.date(int(year), int(month), int(day))
    date = get_object_or_404(models.Date, date=date_num)

    if date.round_set.count() == 0:
        new_game = 1
    else:
        new_game = int(date.round_set.last().round[0]) + 1
    return render(request, 'hisakata/detail.html', {'date': date, 'new_game': new_game, 'youbi': youbi})


def formview(request, year, month, day, round_n):
    date = datetime.date(int(year), int(month), int(day))
    extra = 10

    if request.method == 'GET':
        logs = []
        playerlist = models.Player.objects.all()
        match = models.Match.objects.filter(round__round=round_n, round__class_date__date=date)
        for mt in match:
            li = [mt.winner, mt.result, "", ""]
            for playing in mt.playing_set.all():
                li[playing.player_num + 1] = playing.player.name
            logs.append(li)
        for _ in range(extra):
            logs.append([0, 0, "", ""])

        if models.Round.objects.filter(round=round_n, class_date__date=date).count() != 0:
            comment = models.Round.objects.get(round=round_n, class_date__date=date).comment
        else:
            comment = "詠)"
        return render(request, 'hisakata/form.html',
                      {'year': year, 'month': month, 'day': day, 'round_num': round_n, 'logs': logs,
                       'playerlist': playerlist, 'comment': comment})

    else:  # request.method == 'POST'
        names = request.POST.getlist('name')
        results = request.POST.getlist('result')
        comment = request.POST['comment']
        round_num = request.POST['round']
        csrf = request.POST.get('csrfmiddlewaretoken')

        if (round_n != round_num and models.Round.objects.filter(round=round_num,
                                                                 class_date__date=date).count() == 1):
            error_message = "適切な試合番号を入力してください。"
            logs = []
            playerlist = models.Player.objects.all()
            match = models.Match.objects.filter(round__round=round_n, round__class_date__date=date)
            for mt in match:
                li = [mt.winner, mt.result, "", ""]
                for playing in mt.playing_set.all():
                    li[playing.player_num + 1] = playing.player.name
                logs.append(li)
            for _ in range(extra):
                logs.append([0, 0, "", ""])

            if models.Round.objects.filter(round=round_n, class_date__date=date).count() != 0:
                comment = models.Round.objects.get(round=round_n, class_date__date=date).comment
            else:
                comment = ""
            return render(request, 'hisakata/form.html',
                          {'year': year, 'month': month, 'day': day, 'round_num': round_n, 'logs': logs,
                           'playerlist': playerlist, 'error_message': error_message, 'comment': comment})



        else:
            if models.Round.objects.filter(round=round_num, class_date__date=date).count() == 0:  # 新規round
                # 新規model作成
                models.Round.objects.create(round=round_num, class_date=models.Date.objects.get(date=date))
                for i in range(len(results)):
                    models.Match.objects.create(round=models.Round.objects.get(round=round_num, class_date__date=date))

            i_match = 0

            round_model = models.Round.objects.get(round=round_num, class_date__date=date)
            match = models.Match.objects.filter(round__round=round_num, round__class_date__date=date)
            roundform = models.RoundForm({'round': round_num, 'comment': comment, 'csrfmiddlewaretoken': csrf},
                                         instance=round_model)
            if roundform.is_valid():
                for mt in match:
                    mform = models.MatchForm(
                        {'winner': request.POST['winner' + str(i_match)], 'result': results[i_match],
                         'csrfmiddlewaretoken': csrf},
                        instance=mt)
                    if not names[2 * i_match] or not names[2 * i_match + 1]:
                        mt.delete()
                    else:
                        if mform.is_valid():
                            for playing in mt.playing_set.all():
                                if models.Player.objects.filter(
                                        name=names[2 * i_match + playing.player_num - 1]).count() == 0:
                                    models.Player.objects.create(name=names[2 * i_match + playing.player_num - 1])

                                player = models.Player.objects.get(name=names[2 * i_match + playing.player_num - 1])
                                playing.player = player

                                playing.save()
                            mform.save()
                    i_match += 1
                while i_match < len(results):
                    if names[2 * i_match] != "" and names[2 * i_match + 1] != "":
                        models.Match.objects.create(round=round_model, winner=request.POST['winner' + str(i_match)],
                                                    result=results[i_match])
                        mt = models.Match.objects.order_by('-id')[0]
                        if models.Player.objects.filter(name=names[2 * i_match]).count() == 0:
                            models.Player.objects.create(name=names[2 * i_match])
                        if models.Player.objects.filter(name=names[2 * i_match + 1]).count() == 0:
                            models.Player.objects.create(name=names[2 * i_match + 1])

                        player1 = models.Player.objects.get(name=names[2 * i_match])
                        models.Playing.objects.create(player=player1, match=mt, player_num=1)
                        player2 = models.Player.objects.get(name=names[2 * i_match + 1])
                        models.Playing.objects.create(player=player2, match=mt, player_num=2)

                    i_match += 1
                roundform.save()

            if models.Match.objects.filter(round__round=round_num, round__class_date__date=date).count() == 0:
                models.Round.objects.get(round=round_num, class_date__date=date).delete()

            return HttpResponseRedirect(reverse("hisakata:detail", kwargs={'year': year,
                                                                           'month': month,
                                                                           'day': day}))


def tableview(request, year, month, grade):
    player = []

    for one in models.Player.objects.all():
        flag = False
        if one.grade == int(grade):
            for match in one.match.all():
                if match.round.class_date.date.year == int(year) and match.round.class_date.date.month == int(month):
                    flag = True
        if flag:
            player.append(one)

    max_num = max([one.match.count() for one in player])

    return render(request, 'hisakata/table.html', {'year': year,
                                                   'month': month,
                                                   'player': player,
                                                   'max_num': range(max_num),
                                                   'grade': int(grade),
                                                   })


def playerview(request):
    gradename = ['未登録', '新入生', '2年生', '3年生', '4年生', '院生・社会人', 'ゲスト']
    year = models.nowyear
    player_models = []
    for one in models.Player.objects.all():
        flag = False
        for match in one.match.all():
            if match.round.class_date.date.year == int(year):
                flag = True
        if flag:
            player_models.append(one)

    if request.method == 'GET':
        players = []
        for player in player_models:
            players.append([player.name, player.grade])

        return render(request, 'hisakata/player.html', {'players': players, 'gradename': gradename, })

    else:
        names = request.POST.getlist('name')
        grades = request.POST.getlist('grade')
        csrf = request.POST.get('csrfmiddlewaretoken')
        i_player = 0
        for one in player_models:
            if one.name != names[i_player] or one.grade != grades[i_player]:
                form = models.PlayerForm(
                    {'name': names[i_player], 'grade': grades[i_player], 'csrfmiddlewaretoken': csrf}, instance=one)
                if form.is_valid():
                    form.save()
            i_player += 1

        return HttpResponseRedirect(reverse("hisakata:player"))
