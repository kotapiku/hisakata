import datetime
from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpRequest

from . import models
from django.template.defaulttags import register

youbi = ['月', '火', '水', '木', '金', '土', '日']
now_year = models.nowyear
now_month = models.nowmonth


@register.filter
def get_item(list, num):
    return list[num]


@login_required
def homeview(request):
    return datelistview(request, now_year, now_month)


@login_required
def yearlist(request):
    years = range(models.startyear, models.nowyear + 1)
    return render(request, 'hisakata/yearlist.html', {
        'years': years,
        'page': 'detail',
        'nowyear': now_year, 'nowmonth': now_month,
    })


@login_required
def monthlistview(request, year):
    if int(year) == models.startyear:
        months = range(models.startmonth, models.nowmonth + 1)
    else:
        months = range(1, models.nowmonth + 1)
    return render(request, 'hisakata/monthlist.html', {
        'months': months,
        'year': year,
        'page': 'detail',
        'nowyear': now_year, 'nowmonth': now_month,
    })


@login_required
def datelistview(request, year, month):
    dates = models.Date.objects.filter(date__year=year).filter(date__month=month)
    caution = []
    for date in dates:
        if date.round_set.count() == 0:
            caution.append(False)
        else:
            caution.append(True)
    return render(request, 'hisakata/datelist.html',
                  {'dates': dates, 'year': year, 'month': month, 'youbi': youbi, 'caution': caution,
                   'page': 'detail', 'nowyear': now_year, 'nowmonth': now_month, })


@login_required
def datecreateview(request, year):
    month = models.nowmonth
    if request.method == 'GET':
        return render(request, 'hisakata/dateform.html',
                      {'year': year, 'month': month, 'page': 'detail', 'nowyear': now_year, 'nowmonth': now_month, })
    else:
        error_message = ''
        date = datetime.date(int(request.POST['date'][:4]), int(request.POST['date'][5:7]),
                             int(request.POST['date'][8:]))

        if models.Date.objects.filter(date=date).count() != 0:
            error_message = '重複する日付は入力できません'
        if datetime.date.today() < date:
            error_message = '未来の日付は入力できません'
        if date.year == int(year) and date.month < models.startmonth:
            error_message = '適切な日付を入力してください'

        if error_message:
            return render(request, 'hisakata/dateform.html',
                          {'year': year, 'month': month, 'error_message': error_message, 'page': 'detail', })
        else:
            form = models.DateForm(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(reverse("hisakata:datelist", kwargs={'year': year, 'month': date.month}))


@login_required
def tableyearlist(request):
    years = range(models.startyear, models.nowyear + 1)
    return render(request, 'hisakata/tableyearlist.html', {
        'years': years,
        'page': 'table',
        'nowyear': now_year, 'nowmonth': now_month,
    })


@login_required
def tablemonthlist(request, year):
    if int(year) == models.startyear:
        months = range(models.startmonth, models.nowmonth + 1)
    else:
        months = range(1, models.nowmonth + 1)
    print(months)
    return render(request, 'hisakata/tablelist.html', {
        'year': year,
        'months': months,
        'page': 'table',
        'nowyear': now_year, 'nowmonth': now_month,
    })


@login_required
def detailview(request, year, month, day):
    date_num = datetime.date(int(year), int(month), int(day))
    date = get_object_or_404(models.Date, date=date_num)

    if date.round_set.count() == 0:
        new_game = 1
    else:
        new_game = int(date.round_set.last().round[0]) + 1
    return render(request, 'hisakata/detail.html',
                  {'date': date, 'new_game': new_game, 'youbi': youbi, 'page': 'detail', 'nowyear': now_year,
                   'nowmonth': now_month, })


@login_required
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
                       'playerlist': playerlist, 'comment': comment, 'page': 'detail', 'nowyear': now_year,
                       'nowmonth': now_month, })

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
                           'playerlist': playerlist, 'error_message': error_message, 'comment': comment,
                           'page': 'detail', 'nowyear': now_year, 'nowmonth': now_month, })



        else:
            if models.Round.objects.filter(round=round_num, class_date__date=date).count() == 0:  # 新規round
                # 新規model作成
                models.Round.objects.create(round=round_num, class_date=models.Date.objects.get(date=date))

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


@login_required
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
                                                   'page': 'table',
                                                   'nowyear': now_year, 'nowmonth': now_month,
                                                   })


@login_required
def playerview(request, grade):
    gradename = ['未登録', '新入生', '2年生', '3年生', '4年生', '院生・社会人', 'ゲスト']
    year = models.nowyear
    player_models = []
    if grade == "":
        grade_n = 0
    else:
        grade_n = int(grade)
    for one in models.Player.objects.filter(grade=grade_n):
        flag = False
        if grade_n >= 5:
            for match in one.match.all():
                if match.round.class_date.date.year == int(year):
                    flag = True
        else:
            flag = True
        if flag:
            player_models.append(one)

    if request.method == 'GET':
        players = []
        for player in player_models:
            players.append(player.name)

        return render(request, 'hisakata/player.html',
                      {'players': players, 'gradename': gradename, 'grade': grade_n, 'page': 'player',
                       'nowyear': now_year, 'nowmonth': now_month, })

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

        return HttpResponseRedirect(reverse("hisakata:player", kwargs={'grade': grade_n, }))

@login_required
def deletemodel(request, year, month, day):
    models.Date.objects.get(date=datetime.date(int(year), int(month), int(day))).delete()

    return datelistview(request, year, month)
