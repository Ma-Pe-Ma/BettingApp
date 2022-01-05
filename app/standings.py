from os import name

from dateutil.tz.tz import datetime_ambiguous
from app import auth
from flask import Blueprint
from flask import redirect
from flask import g
from flask import flash
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from app.db import get_db
from app.auth import login_required

bp = Blueprint("standings", __name__, '''url_prefix="/group"''')

from datetime import timezone, datetime
from datetime import timedelta
from dateutil import tz
from collections import namedtuple

from app.configuration import starting_bet_amount
from app.configuration import group_deadline_time, group_evaluation_time

from app.tools.score_calculator import get_group_win_amount
from app.tools.score_calculator import get_group_and_final_bet_amount
from app.tools.score_calculator import get_daily_points_by_current_time
from app.tools.group_calculator import get_final_bet
from app.tools.ordering import order_current_player_standings

Player = namedtuple("Player", "nick, days")
Day = namedtuple("Day", "year, month, day, point")
CurrentPlayerStanding = namedtuple("CurrentPlayerStanding", "name, point")

@bp.route("/standings", methods=("GET",))
@login_required
def standings():
    players = []

    current_player_standings = []

    #create unique time objects
    group_deadline_time_object = datetime.strptime(group_deadline_time, "%Y-%m-%d %H:%M")
    two_days_before_deadline = group_deadline_time_object - timedelta(days=2)
    one_day_before_deadline = group_deadline_time_object - timedelta(days=1)
    group_evaluation_time_object = datetime.strptime(group_evaluation_time, "%Y-%m-%d %H:%M")

    utc_now = datetime.now(tz=timezone.utc)
    utc_now = utc_now.replace(tzinfo=tz.gettz('UTC'))

    #iterate through users
    for player in get_db().execute("SELECT username FROM user", ()):
        user_name = player["username"]

        # find group bet/win amount
        group_bet_amount = get_group_and_final_bet_amount(user_name)
        group_winning_amount = get_group_win_amount(user_name)

        days = []

        #two days before starting show start amount, same for everyone
        amount = starting_bet_amount
        days.append(Day(year=two_days_before_deadline.year, month=two_days_before_deadline.month-1, day=two_days_before_deadline.day, point=amount))        

        #one day before starting show startin minus group+final betting amount
        amount -= group_bet_amount
        days.append(Day(year=one_day_before_deadline.year, month=one_day_before_deadline.month-1, day=one_day_before_deadline.day, point=amount))

        prev_date = group_deadline_time_object
        prev_amount = amount

        #generate in/out points per day for user
        day_prefabs = get_daily_points_by_current_time(user_name)

        # iterate thorugh the days to
        for day_prefab in day_prefabs:
            # calculate the daily point difference
            daily_point = 0
            for point in day_prefab.points:
                daily_point += point

            day_date = datetime.strptime(day_prefab.date, "%Y-%m-%d")

            # if there's a break between matchdays fill the days during break with the last matchdays result
            while (True):
                prev_date += timedelta(days=1)

                if prev_date.date() < day_date.date():
                    days.append(Day(year=prev_date.year, month=prev_date.month-1, day=prev_date.day, point=prev_amount))
                else:
                    break

            # add the examined day to the chart
            amount += daily_point
            days.append(Day(year=day_date.year, month=day_date.month-1, day=day_date.day, point=amount))

            # if the current day is the group evaulation day add a new (fake) day which shows the group bet point win amounts
            if day_date.date() == group_evaluation_time_object.date() and utc_now > group_evaluation_time_object.replace(tzinfo=tz.gettz('UTC')):
                amount += group_winning_amount
                fake_day = day_date + timedelta(days=1)
                days.append(Day(year=fake_day.year, month=fake_day.month-1, day=fake_day.day, point=amount))
                prev_date = fake_day
            else:
                prev_date = day_date

            prev_amount = amount

        final_bet_object = get_final_bet(user_name=user_name)

        # if there's a final result then display it on a new day
        if final_bet_object is not None and final_bet_object.success is not None:
            if final_bet_object.success == 1:
                amount += final_bet_object.betting_amount * final_bet_object.multiplier
            elif final_bet_object.success == 2:
                pass
            
            day_after_finnish = prev_date + timedelta(days=1)
            days.append(Day(year=day_after_finnish.year, month=day_after_finnish.month-1, day=day_after_finnish.day, point=amount))

        #add the last/current player point to seperate list which will be used in a list-chart
        current_player_standings.append(CurrentPlayerStanding(name=user_name, point=days[-1].point))

        day_prefabs.clear()

        players.append(Player(nick=user_name, days=days))

    #order the current player standings by the points
    current_player_standings.sort(key=order_current_player_standings, reverse=True)

    return render_template("standings.html", username = g.user["username"], admin=g.user["admin"], players=players, current_player_standings=current_player_standings)

#https://canvasjs.com/html5-javascript-line-chart/
#https://stackoverflow.com/questions/35854244/how-can-i-create-a-horizontal-scrolling-chart-js-line-chart-with-a-locked-y-axis