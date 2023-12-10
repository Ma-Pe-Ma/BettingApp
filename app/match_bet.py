from flask import Blueprint
from flask import redirect
from flask import g
from flask import flash
from flask import render_template
from flask import request
from flask import url_for

from app.auth import login_required
from app.db import get_db

from app.tools import time_determiner

from sqlalchemy import text

bp = Blueprint('match', __name__, '''url_prefix="/match"''')

@bp.route('/match', methods=('GET', 'POST'))
@login_required
def match_bet():
    try:
        match_id = request.args.get('matchID') if request.args.get('matchID') is not None else request.form['matchID']
    except:
        match_id = None    

    query_string = text("WITH match_state AS ("
                        "SELECT match.id, match.odd1, match.oddX, match.odd2, match.round, match.max_bet, "
                        "tr1.translation AS team1, tr2.translation AS team2, "
                        "date(match.time || :timezone) AS date, strftime('%H:%M', time(match.time || :timezone)) AS time, (strftime('%w', match.time) + 6) % 7 AS weekday, "
                        "(unixepoch(:now) > unixepoch(match.time)) as started "
                        "FROM match "
                        "LEFT JOIN team_translation AS tr1 ON tr1.name = match.team1 AND tr1.language = :l "
                        "LEFT JOIN team_translation AS tr2 ON tr2.name = match.team2 AND tr2.language = :l "
                        "WHERE match.id = :match_id )"

                        "SELECT match_state.*, match_bet.bet, match_bet.goal1, match_bet.goal2 "
                        "FROM bet_user "
                        "LEFT JOIN match_state ON match_state.id = :match_id "
                        "LEFT JOIN match_bet ON match_bet.username = bet_user.username AND match_bet.match_id = :match_id "
                        "WHERE bet_user.username = :u ")

    result = get_db().session.execute(query_string, {'match_id' : match_id, 'now' : time_determiner.get_now_time_string(), 'u' : g.user['username'], 'l' : g.user['language'], 'timezone' : g.user['timezone']})
    match_from_db = result.fetchone()._asdict()

    if match_from_db['started'] is None or match_from_db['started'] > 0:
        return redirect(url_for('home.homepage', match=match_from_db))

    if request.method == 'GET':        
        return render_template('/match-bet.html', match=match_from_db)

    elif request.method == 'POST':
        try:
            bet_value = max(0, min(int(request.form['bet']), match_from_db['max_bet']))
        except ValueError:
            flash('invalid_bet')
            return render_template('/match-bet.html', match=match_from_db)
        try:
            goal1 = int(request.form['goal1'])
            goal2 = int(request.form['goal2'])

            if goal1 < 0 or goal2 < 0:
                raise ValueError('Negative goal specified...')

        except ValueError:
            flash('invalid_goal')
            return render_template('/match-bet.html', match=match_from_db)

        query_string = text("INSERT OR REPLACE INTO match_bet (match_id, username, bet, goal1, goal2) VALUES(:m, :u, :b, :g1, :g2)")
        get_db().session.execute(query_string, {'m' : match_id, 'u' : g.user['username'], 'b' : bet_value, 'g1' : goal1, 'g2' : goal2})
        get_db().session.commit()

        return redirect(url_for('home.homepage', match=match_from_db))