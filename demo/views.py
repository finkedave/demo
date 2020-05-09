from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponseBadRequest
import json
from django.conf import settings
from django.http.response import JsonResponse
from django.utils.module_loading import import_string
from django.http import Http404
from django.http import HttpResponse
import copy
from django.shortcuts import redirect
from . models import Game, Session
from random import seed
from random import random
from random import shuffle, sample, randint
from django.views import View
from django.shortcuts import get_object_or_404

@require_GET
def get_game_state(request, session_name):
    try:
        game = Session.objects.get(session_name=session_name).current_game
        return JsonResponse(json.loads(game.state))
    except Session.DoesNotExist:
        return JsonResponse({"end_session": True})

@require_POST
def next_game(request, session_name):
    session = Session.objects.get(session_name=session_name)
    create_new_game(session=session)
    return JsonResponse({"success": True})

@require_POST
def end_session(request, session_name):
    try:
        Session.objects.get(session_name=session_name).delete()
    except Session.DoesNotExist:
        pass
    return JsonResponse({"end_session": True})

def get_playfield(request, session_name):
    session_qs = Session.objects.filter(session_name=session_name)
    if not session_qs:
        session = Session.objects.create(session_name=session_name, used_playfield_cards="[]")
    else:
        session = session_qs[0]

    if not session.current_game:
        create_new_game(session=session)
    context = {"game": session.current_game, "session_name": session_name, "settings": json.loads(session.settings)}
    return render(request=request, template_name="playfield.html", context=context)

@require_POST
def update_settings(request, session_name):
    session = get_object_or_404(Session, session_name=session_name)
    new_settings = json.loads(request.POST['settings'])
    session.settings = json.dumps(new_settings)
    session.save()
    return next_game(request, session_name)

@require_POST
def make_guess(request, session_name):
    session = Session.objects.get(session_name=session_name)
    guess = request.POST.get("agent_index")
    game = session.current_game
    settings = json.loads(session.settings)
    state = json.loads(game.state)

    if state["turn"].endswith("_win"):
        return JsonResponse({"success": True})

    guessed_agent = state["agents"][int(guess)]
    guessed_agent["revealed"] = True

    game_is_over, state = is_game_over_check(state, guessed_agent, settings)
    if not game_is_over:
        turn = state["turn"]
        if not state["sudden_death"] and turn != guessed_agent["agent"]:
            state = _end_turn(state)
    else:
        state["game_over"] = True;

    game.state = json.dumps(state)
    game.save()
    return JsonResponse({"success": True})

def is_game_over_check(state, guessed_agent, settings):
    red_hidden = False
    blue_hidden = False
    for agent in state["agents"]:
        agent_color = agent["agent"]
        if agent_color=="red" and not agent["revealed"]:
            red_hidden = True
        elif agent_color=="blue" and not agent["revealed"]:
            blue_hidden = True
        elif agent_color=="assassin" and agent["revealed"] and not state["sudden_death"]:
            if settings["assassins_ending"]:
                state["sudden_death"] = True
                return False, state
            else:
                opposing_team = "red" if state["turn"] == "blue" else "blue"
                state["turn"] = opposing_team + "_win"
                return True, state

    turn = state["turn"]
    if state["sudden_death"] and turn != guessed_agent["agent"]:
        if turn == "red":
            state["turn"] = "blue_win"
        else:
            state["turn"] = "red_win"
        return True, state

    if (red_hidden and blue_hidden) or (settings["assassins_ending"] and not state["sudden_death"]):
        return False, state

    if not red_hidden and turn=="red":
        state["turn"] = "red_win"
        return True, state
    elif not blue_hidden and turn=="blue":
        state["turn"] = "blue_win"
        return True, state
    return False, state


@require_POST
def end_turn(request, session_name):
    session = Session.objects.get(session_name=session_name)
    game = session.current_game
    state = json.loads(game.state)
    _end_turn(state=state)
    game.state = json.dumps(state)
    game.save()
    return JsonResponse({"success": True})

def _end_turn(state):
    state["turn"] = "red" if state["turn"] == "blue" else "blue"
    return state

class CreateJoinSession(View):
    def get(self, request):
        return render(request=request, template_name="lobby.html", context={})

    def post(self, request):
        session_name = request.POST.get("session_name", None)
        session = Session.objects.filter(session_name=session_name)
        if not session:
            session = Session.objects.create(session_name=session_name, used_playfield_cards="[]")
            create_new_game(session)
        return redirect('get_playfield', session_name=session_name)


def create_new_game(session):
    all_cards = set([index for index in range(1, 241)])
    used_cards = set(json.loads(session.used_playfield_cards))
    available_cards = all_cards.difference(used_cards)
    if len(available_cards) < 20:
        available_cards = all_cards
        used_cards = set()

    playfield_cards = sample(available_cards, 20)
    agents = []
    agent_indexes = [index for index in range(0, 20)]

    red_agents = agent_indexes[0:7]
    blue_agents = agent_indexes[7:14]
    neutral_agents = agent_indexes[14:18]
    assassin = agent_indexes[18]
    double_agent = agent_indexes[19]
    turn = None
    for index in range(0, 20):
        if index in red_agents:
            agent = "red"
        elif index in blue_agents:
            agent = "blue"
        elif index in neutral_agents:
            agent = "neutral"
        elif index  == assassin:
            agent = "assassin"
        else:
            if randint(0, 1) == 0:
                agent = turn = "blue"
            else:
                agent = turn = "red"
        agents.append({"revealed": False, "agent": agent})
    shuffle(agents)
    state = {"agents": agents, "turn": turn, "game_over": False, "sudden_death": False}
    game = Game.objects.create(state=json.dumps(state), playfield_cards=json.dumps(playfield_cards))
    state = json.loads(game.state)
    state["game_id"] = game.id
    game.state = json.dumps(state)
    game.save()
    used_cards.update(playfield_cards)
    session.used_playfield_cards = json.dumps(list(used_cards))
    session.current_game = game
    session.save()