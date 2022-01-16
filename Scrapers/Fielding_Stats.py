from Utils.Basic_Utils import Basic_Utils as BU
from bs4 import BeautifulSoup, Comment
from Utils.Constants import Constants
import re


class Fielding_Stats:

    def __init__(self, db, season):
        self.db = db
        self.season = season

    def fielding_page(self, url, team):
        """Extracts all of the tables from the fielding page. Well, almost all
        of them. Some we ignore.

        Args:
            url (str): url link to the teams fielding stats page.
            team (str): team we are pulling the stats for.
        """
        fielding_soup = BU.get_soup(url)

        # all of these tables are in the comments..
        comments = fielding_soup.find_all(string=lambda text: isinstance(
            text, Comment))
        for comment in comments:

            # catcher is a bit special bc could be mixed up with cf. Check this
            # first.
            if "Standard Fielding--C" in comment and \
                    not "Standard Fielding--CF" in comment:
                tbody_tag = BeautifulSoup(
                    comment, features="lxml").find('tbody')
                self.handle_fielding(
                    tbody_tag, team, "fielding_catcher", comments)

            # then check the rest of the tables if its not catcher.
            else:
                for table in Constants.fielding_tables.keys():
                    if table in comment:
                        tbody_tag = BeautifulSoup(
                            comment, features="lxml").find('tbody')
                        self.handle_fielding(
                            tbody_tag, team, Constants.fielding_tables[table],
                            comments)

    def handle_fielding(self, tbody_tag, team, table, comments):
        """This one is a doozy bc we need to read multiple tables
        for each position.

        Args:
            tbody_tag (bs4): tbody tag with the first table we are grabbing
            team (str): name of team we are pulling data for.
            table (str): db name of table we are populating
            comments (list of strings): comments that contain the stat tables.
        """
        # same old story. tr tags each player
        tr_tags = tbody_tag.find_all('tr', attrs={'class': None})
        tr_tags += tbody_tag.find_all('tr', attrs={'class': "non_qual"})

        for tag in tr_tags:
            insert_command = """
            INSERT INTO {} VALUES({}, """.format(table, self.season)

            # for fielding totals theres a summary stat that takes place.
            # in the th tag. don't care about it. skip.
            # Also a brutal hack to get rid of &nbsp; tag
            th_tag = tag.find('th')
            try:
                link = th_tag.find('a')['href']
                name = BU.format_name(th_tag.find('a').text)

                insert_command += '"{}", "{}", "{}", '.format(
                    name, team, link)
            except TypeError:
                continue

            # Now each stat.
            td_tags = tag.find_all("td")
            for tag in td_tags:

                # kill % symbol on percentages.
                if "%" in str(tag.text):
                    insert_command += "{}, ".format(tag.text[:-1])

                # otherwise all other stats pretty simple.
                else:
                    insert_command = BU.append_stat_to_statement(
                        tag.text, insert_command)

            # now we want to find the advanced fielding table and append those
            # stats.
            # no need for advanced stats if doing totals... skip it.
            if table == "fielding_totals":
                pass

            elif table == "fielding_catcher":
                for comment in comments:
                    if "Advanced Fielding -- C" in comment and not "Advanced Fielding -- CF" in comment:
                        soup = BeautifulSoup(comment, features="lxml")
                        insert_command += self.fielding_additional_tables(
                            soup.find('tbody'), name,
                            [r'\"PB\"', r'\"WP\"', r'\"SB\"', r'\"CS\"',
                                r'\"caught_stealing_perc\"', r'\"A_tot\"',
                                r'\"E_tot\"', r'\"PO_tot\"', r'\"DP_tot\"'])

            else:
                for comment in comments:
                    if Constants.advanced_tables[table]["html name"] in comment:
                        soup = BeautifulSoup(comment, features="lxml")
                        insert_command += self.fielding_additional_tables(
                            soup.find('tbody'), name,
                            Constants.advanced_tables[table]["repeat stats"])

            insert_command = BU.format_insert_end(insert_command)
            self.db.execute_insert(insert_command)

    def fielding_additional_tables(self, table, name, repeat_stats):
        """Handles the additional tables for fielding.
        Args:
            table (bs4): tbody tag for the additional table.
            name (str): name of player unformatted (has &nbsp;)
            repeat_stats (str): list of regex commands taht filter out repeated
            stats.

        Returns:
            str: partial insertion command string with stats.
        """
        tr_tags = table.find_all('tr', attrs={'class': None})
        tr_tags += table.find_all('tr', attrs={'class': "non_qual"})

        insert_command = ""
        name = BU.unformat_name(name)
        for tag in tr_tags:
            # make sure its the same player.
            # ugh i think we need the nbsp in order for this to work.
            if tag.find('th').text == name:
                td_tags = tag.find_all('td')

                for tag in td_tags:
                    # check for repeat stats
                    if self.check_repeat_stat(repeat_stats, tag):
                        continue

                    if "%" in str(tag.text):
                        insert_command += "{}, ".format(tag.text[:-1])

                    # age column keeps getting repeated...
                    elif 'data-stat="age"' in str(tag):
                        continue

                    else:
                        try:
                            float(tag.text)
                            insert_command += "{}, ".format(tag.text)

                        except ValueError:
                            insert_command += '"{}", '.format(tag.text)

        return insert_command

    def check_repeat_stat(self, repeat_stats, tag):
        for stat in repeat_stats:
            if re.search(stat, str(tag)):
                return True
        return False
