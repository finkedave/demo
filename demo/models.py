from django.db import models
from django.utils.translation import gettext as _
import json

class Game(models.Model):
    state = models.TextField()
    playfield_cards = models.TextField()

    def get_playfield_cards(self):
        return json.loads(self.playfield_cards)
class Session(models.Model):
    session_name = models.TextField()
    current_game = models.ForeignKey(Game, null=True, on_delete=models.SET_NULL)
    used_playfield_cards = models.TextField()


