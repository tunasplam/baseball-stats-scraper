"""
Pitching stats
"""

from Utils.Basic_Utils import Basic_Utils as BU
from Utils.Constants import Constants
from bs4 import BeautifulSoup, Comment


class Pitching_Stats:

    def __init__(self, db, season):
        self.db = db
        self.season = season

    def pitching_page(self, url, team):
        """Deals with extracting the tables from the pitching page.

        Args:
            url (str): url link to the teams where fielding stats page.
            team (str): team we are pulling the stats for.
        """
        pitching_soup = BU.get_soup(url)

        # player_pitching only table not in the comments.
        tbody_tag = pitching_soup.find('tbody')
        BU.handle_player_table(
            self.season, tbody_tag, team, "player_pitching", self.db)

        # all other tables in comments.
        comments = pitching_soup.find_all(string=lambda text: isinstance(
            text, Comment))
        for comment in comments:
            for table in Constants.pitching_tables.keys():
                if table in comment:
                    tbody_tag = BeautifulSoup(comment, features="lxml").find(
                        'tbody')
                    BU.handle_player_table(
                        self.season, tbody_tag,
                        team, Constants.pitching_tables[table], self.db)

    def boxscores_pitching(self, soup, team, game_num):
        """Gets pithcing from boxscores and puts in db.

        Args:
            soup (bs4): the comment holding the table for the pitcing info
            team (str): team name code
            game_num (int): season game number for the team
        """
        # pitching.. only want the ones in tbody.
        tr_tags = soup.find('tbody').find_all('tr', class_=None)

        for tr_tag in tr_tags:

            # each tag is another player
            insert_command = """
            INSERT INTO boxscores_pitching
            VALUES({}, "{}", "{}", """.format(self.season, team, game_num)

            for tag in tr_tag:

                # player name and link to page are found
                # in the only th tag (has specific attr)
                if tag.has_attr('data-append-csv'):
                    # Pitcher name
                    insert_command += '"{}", '.format(
                        BU.format_name(tag.find('a').text))

                    # Get the link to the player page
                    insert_command += '"{}", '.format(
                        Constants.URL_ROOT + tag.find('a')['href'])

                elif "%" in str(tag.text):
                            insert_command += "{}, ".format(tag.text[:-1])

                # everything here is nice easy numbers.
                else:
                    # Instances such as N/A BAs or offensive stats for pitchers
                    # will be populated as NULL.
                    if len(tag.text) == 0:
                        insert_command += "NULL, "
                    # if the text if 'inf' (infinity) just put NULL
                    elif tag.text == 'inf':
                        insert_command += "NULL, "
                    else:
                        insert_command += "{}, ".format(tag.text)

            insert_command = BU.format_insert_end(insert_command)
            self.db.execute_insert(insert_command)
