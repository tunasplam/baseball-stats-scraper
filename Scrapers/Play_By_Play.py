"""
FOR NOW, NOT BEING USED. EVERYTHING IS IN BOXSCORES.py

populates:
play_by_play
"""

from Utils.Basic_Utils import Basic_Utils as BU
from Utils.Constants import Constants
from bs4 import BeautifulSoup, Comment
import re
import sys


class Play_By_Play:

    def __init__(self, db, season):
        self.db = db
        self.season = season

    def play_by_play(self, team):
        """
        Go through the schedules then check each game. If the
        boxscore already has an entry in the db, don't even dl the page.
        """

        # First get the soup for the schedule html...
        url = "https://www.baseball-reference.com/teams/" + team + "/" \
              + str(self.season) + "-schedule-scores.shtml"
        print(url)

        schedule_soup = BU.get_soup(url)

        # Game-by-Game Schedule table. Get with bs. Nicely within a tbody.
        tbody = schedule_soup.find_all('tbody')

        games = tbody[0].find_all('tr')

        for game in games:
            # th has the game num. See if we need to skip.
            game_num_tag = game.find('th')
            if "aria-label" in str(game_num_tag):
                continue

            boxscore_link = game.find(
                'td', {'data-stat': 'boxscore'}).find('a')['href']

            # check if the game already entered.
            results = self.db.execute_select(
                """SELECT * FROM play_by_play WHERE boxscore_link = "{}";
                """.format(boxscore_link))

            if len(results) > 0:
                print("Skipping ", boxscore_link)
                continue

            self.get_play_by_play(boxscore_link)

    def get_play_by_play(self, url):
        """handle_play_by_play gives the boxscore link to this function
        which actually gets the play by play data.

        TODO need to lookup the link to the batter and pitcher!

        Args:
            url (str): url to play by play data for a game.
        """
        boxscore_soup = BU.get_soup(Constants.URL_ROOT + url)

        # Once again, our table is commented out...
        comments = boxscore_soup.find_all(string=lambda text: isinstance(
            text, Comment))
        for comment in comments:

            # Will grab the correct table. TODO??
            # not sure if this todo still applies it is ancient.
            if re.search(r'Play by Play Table', str(comment)):
                boxscore_soup = BeautifulSoup(comment, features="lxml")

        # all the events have id="event_{num}" and class="{top/bottom}_inning"
        event_tags = boxscore_soup.find_all('tr', class_="top_inning")
        event_tags += boxscore_soup.find_all('tr', class_="bottom_inning")

        for tag in event_tags:
            insert_command = """
            INSERT INTO play_by_play
            VALUES({}, "{}", """.format(self.season, url)

            td_tags = tag.find_all('td')

            # inning is in th tag
            insert_command += '"{}", '.format(tag.find('th').text)

            for td_tag in td_tags:

                # these three pieces of info in the same tag
                if "pitches_pbp" in str(td_tag):
                    # pitch count can be null during pick offs.
                    try:
                        pit = re.findall(r'(?<=^)[0-9].*?(?=,)', td_tag.text)[0]
                    except IndexError:
                        pit = "NULL"
                    try:
                        cnt = re.findall(r'\([0123]-[012]\)', td_tag.text)[0]
                    except IndexError:
                        cnt = "NULL"

                    # The mysterious ascii char 160 at play here again.
                    # pitch sequence is all the chars after 160
                    # SUPPPER hacky i know...
                    try:
                        pitch_sequence_str = re.findall(
                            r'(?<=\w).*?(?=$)', td_tag.text)[0]
                        pitch_sequence = ""
                        add = False
                        for char in pitch_sequence_str:
                            if add:
                                pitch_sequence += char
                            if ord(char) == 160:
                                add = True
                    except IndexError:
                        pitch_sequence = "NULL"

                    insert_command += '{}, "{}", "{}", '.format(
                        pit, cnt, pitch_sequence)

                # for the probabilities, strip the % symbol and convert to int.
                elif "win_probability_added" in str(td_tag) or \
                     "win_expectancy_post" in str(td_tag):
                    insert_command += "{}, ".format(td_tag.text[:-1])

                else:
                    insert_command = BU.append_stat_to_statement(
                        td_tag.text, insert_command)

            insert_command = BU.format_insert_end(insert_command)
            if self.db.execute_insert(insert_command) == 2:
                print("examine the table on this url: \n {}".format(
                    Constants.URL_ROOT + url))
                sys.exit(1)

