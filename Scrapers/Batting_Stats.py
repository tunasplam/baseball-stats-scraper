"""
All the batting stats

populates all batting AND baserunning tables.
"""
from Utils.Basic_Utils import Basic_Utils as BU
from bs4 import BeautifulSoup, Comment
from Utils.Constants import Constants


class Batting_Stats:

    def __init__(self, db, season):
        self.db = db
        self.season = season

    def batting_page(self, url, team):
        """Handles extraction of all the tables for batting stats page.

        Args:
            url (str): url for the teams batting stats page.
            team (str): team we are pulling stats for.
        """
        batting_soup = BU.get_soup(url)

        # player_batting is first tbody tag that is not in comments.
        tbody_tag = batting_soup.find('tbody')
        BU.handle_player_table(
            self.season, tbody_tag, team, "player_batting", self.db)

        # rest of the tables are in comments.
        comments = batting_soup.find_all(string=lambda text: isinstance(
            text, Comment))
        for comment in comments:
            for table in Constants.batting_tables.keys():
                if table in comment:
                    tbody_tag = BeautifulSoup(comment, features="lxml").find(
                        'tbody')
                    # this handles the actually insertion.
                    BU.handle_player_table(
                        self.season, tbody_tag,
                        team, Constants.batting_tables[table], self.db)

    def boxscores_batting(self, soup, team, game_num):
        """Gets the batting box scores and puts in db.
        Args:
            soup (bs4): comment that holds table for batting stats
            team (str): team code for name
            game_num (int): season game number for team
        """
        # batting.. only want the ones in tbody.
        tr_tags = soup.find('tbody').find_all('tr', class_=None)

        pos = 1
        for tr_tag in tr_tags:

            # Each tr tag is another player.
            insert_command = """
            INSERT INTO boxscores_batting
            VALUES({}, "{}", {}, """.format(self.season, team, game_num)

            for tag in tr_tag:

                # player name is in the only a tag, so this one is easy.
                # position is also in the same tag. can also find if starter.
                # Only th has the attr below...
                if tag.has_attr('data-append-csv'):
                    # Pitcher name
                    insert_command += '"{}", '.format(
                        BU.format_name(tag.find('a').text))

                    # Get the link to the player page
                    insert_command += '"{}", '.format(tag.find('a')['href'])

                    # this little bit of re gets the position.
                    # can also figure out which pticher started here.
                    # if th text indented then not starter.
                    # I know this is hacky by first char of subs has
                    # ord value of 160..
                    if ord(tag.text[0]) == 160:
                        insert_command += "0, "
                    else:
                        insert_command += "1, "
                        # if its a starter, increment order in starting lineup.
                        pos += 1
                    # Now we can put in the position.
                    # Note if AL then no pitcher,
                    # so check if pos > 9.
                    if pos <= 9:
                        insert_command += "{}, ".format(pos)
                    else:
                        insert_command += "0, "

                elif "details" in str(tag):
                    insert_command += '"{}", '.format(tag.text)

                elif "%" in str(tag.text):
                    insert_command += "{}, ".format(tag.text[:-1])

                # Now.. everything here on out is straight forward
                else:
                    # Instances such as N/A BAs or offensive stats for pitchers
                    # will be populated as NULL.
                    if len(tag.text) == 0:
                        insert_command += "NULL, "
                    else:
                        insert_command += "{}, ".format(tag.text)

            insert_command = BU.format_insert_end(insert_command)
            self.db.execute_insert(insert_command)
