"""
Gets the "basic stats"

populates:
player_info
teams
schedules
"""

from Utils.Basic_Utils import Basic_Utils as BU
from Utils.Constants import Constants
import re


class Basic_Stats:

    def __init__(self, db, season):
        self.db = db
        self.season = season

    def get_player_info(self, team):
        """Populates the player's entries in player_info table.

        Args:
            team (str): Team code we are inserting entry for
        """
        # need to go to the roster page.
        url = "https://www.baseball-reference.com/teams/" + team + "/" \
              + str(self.season) + "-roster.shtml"
        soup = BU.get_soup(url)

        # player_info is the first tbody tag
        # newer seasons have a 'ranker' table first. This is true for seasons
        # past 2021.
        if self.season >= 2021:
            table_tag = soup.find_all('tbody')[1]
        else:
            table_tag = soup.find_all('tbody')[0]

        # each tr tag another play
        tr_tags = table_tag.find_all('tr')

        for tr_tag in tr_tags:
            insert_command = "INSERT INTO player_info VALUES({}, ".format(
                self.season)

            # player name, link, and team... all in th tag.
            tag = tr_tag.find('th')
            link = tag.find('a')['href']
            name = BU.format_name(tag.find('a').text)
            insert_command += '"{}", "{}", "{}", '.format(
                name, team, link)

            td_tags = tr_tag.find_all('td')
            for tag in td_tags:
                # escape the , char in d.o.b.
                if "date_of_birth" in str(tag):
                    dob = re.sub(r',', r'', tag.text)
                    insert_command += '"{}", '.format(dob)

                # for years xp, switch 1st to 1
                elif "experience" in str(tag):
                    if tag.text == "1st":
                        insert_command += "1, "
                    else:
                        insert_command += "{}, ".format(tag.text)

                # height.. straight inches.
                elif "height" in str(tag):
                    insert_command += "{}, ".format(tag['csk'])

                else:
                    insert_command = BU.append_stat_to_statement(
                        tag.text, insert_command)

            insert_command = BU.format_insert_end(insert_command)
            self.db.execute_insert(insert_command)

    def populate_teams(self):
        """fills in the teams table with stuff from Constants.teams
        """
        for team in Constants.teamInfo:
            insert_command = "INSERT INTO teams VALUES ({}, ".format(
                self.season)
            insert_command += '"{}", "{}", "{}", "{}", "{}", "{}");'.format(
                team,
                Constants.teamInfo[team]["league"],
                Constants.teamInfo[team]["division"],
                Constants.teamInfo[team]["TZ"],
                Constants.teamInfo[team]["full name"],
                Constants.teamInfo[team]["name"])

            self.db.execute_insert(insert_command)

    def game_by_game_schedule_table(self, team, game_num, game):
        """Fill in schedules table from season schedule page.

        Args:
            team (str): team we are getting stats for
            game_num (int): number game for team we are getting stats for
            game (bs4): tag for schedule table.
        """

        insert_command = """
            INSERT INTO schedules
            VALUES ({}, "{}", {}, """.format(
            self.season, team, game_num)

        td_tags = game.find_all('td')
        for tag in td_tags:
            text = ""

            # if pitcher... get the name from title info.
            # also link to their page.
            if "pitcher" in str(tag):
                # Name is in the a tag. Find the title of that tag.
                if tag.find('a'):
                    name = BU.format_name(tag.find('a')['title'])
                    insert_command += '"{}", '.format(name)
                    text = tag.find('a')['href']
                else:
                    insert_command += '"", '

            # boxscore, we want the link
            elif "boxscore" in str(tag):
                text = tag.find('a')['href']

            # extra_innings, we want the csk value
            elif "extra_innings" in str(tag):
                text = tag['csk']

            # attendance, kill the comma
            elif "attendance" in str(tag):
                text = re.sub(",", "", tag.text)

            # win_loss_streak we want the csk value
            elif "win_loss_streak" in str(tag):
                text = tag['csk']

            # day's standings. Tricky bc date also here.
            elif "date_game" in str(tag):
                insert_command += '"{}", '.format(tag.text)
                text = tag.find('a')['href']

            # already did team_id, skip
            elif "team_ID" in str(tag):
                continue

            else:
                text = tag.text

            insert_command = BU.append_stat_to_statement(
                text, insert_command)

        # now that we have the runs per innings info that is populated...
        # fill those in with blanks for now.
        insert_command += ('"", ' * 28)

        insert_command = BU.format_insert_end(insert_command)
        self.db.execute_insert(insert_command)
