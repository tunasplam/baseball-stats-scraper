"""
    All the constants, all in one place.
    Now nicely formatted for your viewing pleasure :)

    TODO will need to start pulling this from baseball reference each season
    to account for older years where league did not have this team
    configuration.

"""

from datetime import timedelta


class Constants:

    URL_ROOT = "https://www.baseball-reference.com"

    teams = ["NYY", "BOS", "TBR", "TOR", "BAL",
             "CLE", "DET", "MIN", "CHW", "KCR",
             "HOU", "SEA", "LAA", "OAK", "TEX",
             "ATL", "PHI", "WSN", "NYM", "MIA",
             "MIL", "CHC", "STL", "PIT", "CIN",
             "ARI", "LAD", "SFG", "COL", "SDP"]
    teamInfo = {
        "NYY": {"league": "AL", "division": "AL_East", "TZ": "EST",
                "full name": "New York Yankees", "name": "Yankees"},
        "BOS": {"league": "AL", "division": "AL_East", "TZ": "EST",
                "full name": "Boston Red Sox", "name": "Red Sox"},
        "TBR": {"league": "AL", "division": "AL_East", "TZ": "EST",
                "full name": "Tampa Bay Rays", "name": "Rays"},
        "TOR": {"league": "AL", "division": "AL_East", "TZ": "EST",
                "full name": "Toronto Blue Jays", "name": "Blue Jays"},
        "BAL": {"league": "AL", "division": "AL_East", "TZ": "EST",
                "full name": "Baltimore Orioles", "name": "Orioles"},
        "CLE": {"league": "AL", "division": "AL_Central", "TZ": "EST",
                "full name": "Cleveland Indians", "name": "Indians"},
        "DET": {"league": "AL", "division": "AL_Central", "TZ": "EST",
                "full name": "Detroit Tigers", "name": "Tigers"},
        "MIN": {"league": "AL", "division": "AL_Central", "TZ": "CST",
                "full name": "Minnesota Twins", "name": "Twins"},
        "CHW": {"league": "AL", "division": "AL_Central", "TZ": "CST",
                "full name": "Chicago White Sox", "name": "White Sox"},
        "KCR": {"league": "AL", "division": "AL_Central", "TZ": "CST",
                "full name": "Kansas City Royals", "name": "Royals"},
        "HOU": {"league": "AL", "division": "AL_West", "TZ": "CST",
                "full name": "Houston Astros", "name": "Astros"},
        "SEA": {"league": "AL", "division": "AL_West", "TZ": "PST",
                "full name": "Seattle Mariners", "name": "Mariners"},
        "LAA": {"league": "AL", "division": "AL_West", "TZ": "PST",
                "full name": "Los Angeles Angels", "name": "Angels"},
        "OAK": {"league": "AL", "division": "AL_West", "TZ": "PST",
                "full name": "Oakland Athletics", "name": "Athletics"},
        "TEX": {"league": "AL", "division": "AL_West", "TZ": "CST",
                "full name": "Texas Rangers", "name": "Rangers"},
        "ATL": {"league": "NL", "division": "NL_East", "TZ": "EST",
                "full name": "Atlanta Braves", "name": "Braves"},
        "PHI": {"league": "NL", "division": "NL_East", "TZ": "EST",
                "full name": "Philadelphia Phillies", "name": "Phillies"},
        "WSN": {"league": "NL", "division": "NL_East", "TZ": "EST",
                "full name": "Washington Nationals", "name": "Nationals"},
        "NYM": {"league": "NL", "division": "NL_East", "TZ": "EST",
                "full name": "New York Mets", "name": "Mets"},
        "MIA": {"league": "NL", "division": "NL_East", "TZ": "EST",
                "full name": "Miami Marlins", "name": "Marlins"},
        "MIL": {"league": "NL", "division": "NL_Central", "TZ": "CST",
                "full name": "Milwaukee Brewers", "name": "Brewers"},
        "CHC": {"league": "NL", "division": "NL_Central", "TZ": "CST",
                "full name": "Chicago Cubs", "name": "Cubs"},
        "STL": {"league": "NL", "division": "NL_Central", "TZ": "CST",
                "full name": "St. Louis Cardinals", "name": "Cardinals"},
        "PIT": {"league": "NL", "division": "NL_Central", "TZ": "EST",
                "full name": "Pittsburgh Pirates", "name": "Pirates"},
        "CIN": {"league": "NL", "division": "NL_Central", "TZ": "EST",
                "full name": "Cincinnati Reds", "name": "Reds"},
        "ARI": {"league": "NL", "division": "NL_West", "TZ": "MST",
                "full name": "Arizona Diamondbacks", "name": "Diamondbacks"},
        "LAD": {"league": "NL", "division": "NL_West", "TZ": "PST",
                "full name": "Los Angeles Dodgers", "name": "Dodgers"},
        "SFG": {"league": "NL", "division": "NL_West", "TZ": "PST",
                "full name": "San Francisco Giants", "name": "Giants"},
        "COL": {"league": "NL", "division": "NL_West", "TZ": "MST",
                "full name": "Colorado Rockies", "name": "Rockies"},
        "SDP": {"league": "NL", "division": "NL_West", "TZ": "PST",
                "full name": "San Diego Padres", "name": "Padres"},
        }

    # these tables are used for finding stat tables on stat pages.. first value
    # the value from the url, second value the name of our table
    batting_tables = {
        "div_players_advanced_batting": "player_advanced_batting",
        "players_baserunning_batting": "baserunning",
        "Team PH/HR/Situ Hitting": "pinch_hit_home_run_situational_hitting",
        "Team Pitches Batting": "pitches_batting",
        "Team Player Value": "player_batter_values"
        }
    pitching_tables = {
        "Team Player Value": "player_pitcher_values",
        "Baserunning/Situ": "pitching_baserunning_and_situations",
        "Pitching Pitches": "pitches_pitcher"
        }
    fielding_tables = {
        "Team Fielding--Totals": "fielding_totals",
        "Standard Fielding--1B": "fielding_first_base",
        "Standard Fielding--2B": "fielding_second_base",
        "Standard Fielding--3B": "fielding_third_base",
        "Standard Fielding--SS": "fielding_ss",
        "Standard Fielding--LF": "fielding_lf",
        "Standard Fielding--CF": "fielding_cf",
        "Standard Fielding--RF": "fielding_rf",
        "Standard Fielding--P": "fielding_pitcher"
        }
    advanced_tables = {
        "fielding_first_base": {
            "html name": "Advanced Fielding -- 1B",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"',
                             r'\"PO_tot\"', r'\"DP_tot\"']
        },
        "fielding_second_base": {
            "html name": "Advanced Fielding -- 2B",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"',
                             r'\"PO_tot\"', r'\"DP_tot\"']
            },
        "fielding_third_base": {
            "html name": "Advanced Fielding -- 3B",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"',
                             r'\"PO_tot\"', r'\"DP_tot\"']
            },
        "fielding_ss": {
            "html name": "Advanced Fielding -- SS",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"',
                             r'\"PO_tot\"', r'\"DP_tot\"']
            },
        "fielding_lf": {
            "html name": "Advanced Fielding -- LF",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"']
            },
        "fielding_cf": {
            "html name": "Advanced Fielding -- CF",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"']
            },
        "fielding_rf": {
            "html name": "Advanced Fielding -- RF",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"']
            },
        "fielding_pitcher": {
            "html name": "Advanced Fielding -- P",
            "repeat stats": [r'\"A_tot\"', r'\"E_tot\"',
                             r'\"PO_tot\"', r'\"DP_tot\"']
            },
        }

    months = ["Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]

    #db_path = "baseball.db"
    day = timedelta(days=1)
