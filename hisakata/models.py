from django.forms import ModelForm
from django.db import models
from django.core.urlresolvers import reverse
import datetime

startyear = 2017
nowyear = datetime.datetime.today().year


class Date(models.Model):
    date = models.DateField()

    def get_absolute_url(self):
        return reverse("hisakata:datelist")

    def __str__(self):
        return str(self.date)


class Round(models.Model):
    class_date = models.ForeignKey('Date', on_delete=models.CASCADE)
    round = models.IntegerField(default=0)

    def admin_date(self):
        return self.class_date.date

    def get_absolute_url(self):
        return reverse("hisakata:detail", kwargs={'year': self.class_date.date.year,
                                                  'month': self.class_date.date.month,
                                                  'day': self.class_date.date.day})

    def __str__(self):
        return str(self.round)


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
        ordering = ('id',)

    def get_absolute_url(self):
        return reverse("hisakata:detail", kwargs={'year': self.round.class_date.date.year,
                                                  'month': self.round.class_date.date.month,
                                                  'day': self.round.class_date.date.day})

    def admin_date(self):
        return self.round.class_date.date

    def player1(self):
        return self.playing_set.get(player_num=1).player.name
        #return Playing.objects.get(match_id=self.id, player_num=1).player.name

    def player2(self):
        return self.playing_set.get(player_num=2).player.name
        #return Playing.objects.get(match_id=self.id, player_num=2).player.name

    def round_id(self):
        return self.round.id


class Player(models.Model):
    name = models.CharField(max_length=20)
    match = models.ManyToManyField('Match', through='Playing', through_fields=('player', 'match'))

    class Meta:
        ordering = ('name',)

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


class DateForm(ModelForm):
    class Meta:
        model = Date
        fields = ['date', ]


class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ['winner', 'result', ]


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', ]


class PlayingForm(ModelForm):
    class Meta:
        model = Playing
        fields = ['player_num', ]
