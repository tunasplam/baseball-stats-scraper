"""
    So now I know a lot more about things. Such as sqlite3. Better webscraping.
    Time to revisit baseball.

    This TODO list should be kept in order that things need to be done.

    X TODO Multithreading
        Each thread handles another team. make a queue of teams to be
        scraped.

        OKAY so multithreading didnt quite work even when we tried
        having multiple temporary dbs.
        I think it is stopped by us having only one needle to write on the
        HDD with.

    O TODO loop table_creator.py in with this program

    O TODO make sure that the schedules table was populated properly

    O TODO test the covid season

    O TODO Maybe split up Boxscores class

"""

from Utils.Constants import Constants
from Utils.Database_Driver import Database_Driver
from Utils.Basic_Utils import Basic_Utils as BU
# these classes below hold all the statistic scraper functions
# TODO figure out from Scrapers import *
from Scrapers.Fielding_Stats import Fielding_Stats
from Scrapers.Basic_Stats import Basic_Stats
from Scrapers.Batting_Stats import Batting_Stats
from Scrapers.Pitching_Stats import Pitching_Stats
from Scrapers.Boxscores import Boxscores


def main():

    # TODO some sort of cli to get the season?
    season = 2021
    db_path = "baseball.db"
    db = Database_Driver(db_path)

    # TODO check if tables are made. if not, run table creator.

    basic_stats = Basic_Stats(db, season)
    batting_stats = Batting_Stats(db, season)
    fielding_stats = Fielding_Stats(db, season)
    pitching_stats = Pitching_Stats(db, season)
    boxscore_stats = Boxscores(
        db, season, batting_stats, pitching_stats)

    # player info comes first. That way no issues with looking up player links
    # in play by play.
    for team in Constants.teams:

        # Player info from roster page.
        basic_stats.get_player_info(team)
        BU.printProgressBar(Constants.teams.index(team) + 1,
                            30, prefix="Player Info", length=50)
    print()

    for team in Constants.teams:
        BU.printProgressBar(0, 172, prefix=team, length=50)

        basic_stats.populate_teams()
        batting_stats.batting_page(
            "https://www.baseball-reference.com/teams/" + team + "/"
            + str(season) + "-batting.shtml", team)
        pitching_stats.pitching_page(
            "https://www.baseball-reference.com/teams/" + team + "/"
            + str(season) + "-pitching.shtml", team)
        fielding_stats.fielding_page(
            "https://www.baseball-reference.com/teams/"
            + team + "/" + str(season) + "-fielding.shtml", team)

        # boxscores and game by game stats.
        url = "https://www.baseball-reference.com/teams/" + team + "/" \
            + str(season) + "-schedule-scores.shtml"
        schedule_soup = BU.get_soup(url)

        # Game-by-Game Schedule table. Get with bs. Nicely within a tbody.
        tbody = schedule_soup.find_all('tbody')

        games = tbody[0].find_all('tr')

        for game in games:
            # th has the game num. See if we need to skip.
            game_num_tag = game.find('th')

            if not "aria-label" in str(game_num_tag):
                game_num = game_num_tag.text

                # get the game info first
                basic_stats.game_by_game_schedule_table(team, game_num, game)

                # do we need to skip?
                boxscore_link = game.find(
                    'td', {'data-stat': "boxscore"}).find('a')['href']

                results = db.execute_command("""
                    SELECT *
                    FROM play_by_play
                    WHERE boxscore_link="{}";
                """.format(boxscore_link))

                if len(results) == 0:
                    # now get boxscores and play by play
                    boxscore_link = Constants.URL_ROOT + boxscore_link

                    boxscore_stats.handle_game(boxscore_link, team, game_num)

                    BU.printProgressBar((int(game_num) + 10),
                                        172, prefix=team, length=50)
        print()

    print("Now filling in the blanks. Will take some time...")
    boxscore_stats.update_play_by_play()


main()
