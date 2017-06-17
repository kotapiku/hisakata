from django.forms import ModelForm
from django.db import models
from django.core.urlresolvers import reverse
import datetime

startyear = 2017
nowyear = datetime.datetime.today().year


class Date(models.Model):
    date = models.DateField()

    def __str__(self):
        return str(self.date)

    class Meta:
        ordering = ['date']


class Round(models.Model):
    class_date = models.ForeignKey('Date', on_delete=models.CASCADE)
    round = models.CharField(default='1', max_length=3)
    comment = models.TextField(default='詠)', null=True, blank=True)

    def admin_date(self):
        return self.class_date.date

    def get_absolute_url(self):
        return reverse("hisakata:detail", kwargs={'year': self.class_date.date.year,
                                                  'month': self.class_date.date.month,
                                                  'day': self.class_date.date.day})

    def __str__(self):
        return str(self.round)

    class Meta:
        ordering = ['round']


class Match(models.Model):
    WINNER_CHOICES = (
        (0, 'Undecided'),
        (1, 'player1'),
        (2, 'player2'),
    )

    round = models.ForeignKey('Round', on_delete=models.CASCADE)
    winner = models.IntegerField(choices=WINNER_CHOICES, default=0)  # player1が勝ちなら1, player2の勝ちなら2, 未定なら0
    result = models.IntegerField(default=0)

    class Meta:
        ordering = ['id']

    def admin_date(self):
        return self.round.class_date.date

    def player1(self):
        return self.playing_set.get(player_num=1).player.name


    def player2(self):
        return self.playing_set.get(player_num=2).player.name


    def round_id(self):
        return self.round.id


class Player(models.Model):
    GRADE_CHOICE = [
        (0, '未登録'),
        (1, '新入生'),
        (2, '2年生'),
        (3, '3年生'),
        (4, '4年生'),
        (5, '院生・社会人'),
        (6, 'ゲスト'),
    ]
    name = models.CharField(max_length=20)
    match = models.ManyToManyField('Match', through='Playing', through_fields=('player', 'match'))
    grade = models.IntegerField(choices=GRADE_CHOICE, default=0)  #基本学年(1-4,5),ゲスト6,未登録0

    class Meta:
        ordering = ['grade']

    def __str__(self):
        return self.name


class Playing(models.Model):
    PLAYER_CHOICES = (
        (1, 'player1'),
        (2, 'player2'),
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player_num = models.IntegerField(choices=PLAYER_CHOICES, default=1)


    @property
    def date(self):
        return self.match.round.class_date.date

    class Meta:
        ordering = ['player_num',]


class DateForm(ModelForm):
    class Meta:
        model = Date
        fields = ['date', ]


class RoundForm(ModelForm):
    class Meta:
        model = Round
        fields = ['round', 'comment', ]


class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ['winner', 'result', ]


class PlayingForm(ModelForm):
    class Meta:
        model = Playing
        fields = ['player', ]


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'grade',]
