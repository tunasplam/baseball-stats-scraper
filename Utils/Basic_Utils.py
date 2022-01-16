"""
Some basic utilities for the project
"""

from bs4 import BeautifulSoup, Comment
import requests


class Basic_Utils:

    def handle_player_table(season, tbody_tag, team, table, db):
        """Deals with grabbing stats and populating db for tables from batting
        and pitching page.

        returns the insertion command
        Args:
            tbody_tag (bs4): tbody tag for the table we are pulling from.
            team (str): team we are pulling stats for.
            table (str): db name for the table we are populating.
            db (DB conn): connection to the database
        """
        # each tr tag another player.
        # We want the ones with no class and the tags
        # where class is non_qual. Other tr tags are dividers or headers.
        tr_tags = tbody_tag.find_all('tr', attrs={'class': None})
        tr_tags += tbody_tag.find_all('tr', attrs={'class': "non_qual"})

        for tr_tag in tr_tags:
            insert_command = "INSERT INTO {} VALUES({}, ".format(
                table, season)

            # th tag has the name, link, and now is the time to put in theteam.
            # player_batting and player_pitching has no th so we have to find
            # data-stat attribute for this info.
            if table == "player_batting" or table == "player_pitching":
                info_tag = tr_tag.find('td', attrs={'data-stat': 'player'})
            else:
                info_tag = tr_tag.find('th')

            try:
                link = info_tag.find('a')['href']
                name = Basic_Utils.format_name(info_tag.find('a').text)
                insert_command += '"{}", "{}", "{}", '.format(
                    name, team, link)
            except TypeError:
                # if type error then we have some weird summary stat. Skip it.
                continue

            # each column a td tag. Some tables have special cases
            # that need to be handled.
            td_tags = tr_tag.find_all('td')
            for tag in td_tags:

                # if percentage stat has a % sign, nix it.
                if "%" in str(tag.text):
                    insert_command += "{}, ".format(tag.text[:-1])

                # if name was in td tag, skip (was handled above)
                elif 'data-stat="player"' in str(tag):
                    continue

                # ERA can be infinite, populate with NULL.
                elif tag.text == 'inf':
                    insert_command += "NULL, "

                # straight copy the info with no shenanigans.
                else:
                    insert_command = Basic_Utils.append_stat_to_statement(
                        tag.text, insert_command)

            insert_command = Basic_Utils.format_insert_end(insert_command)
            db.execute_insert(insert_command)

    def append_stat_to_statement(text, insert_command):
        """when appending a stat to an insert statement:
        strings need to be nested in ""
        ints can be left alone

        Args:
            tag (str): containing the stat in question
            insert_command (str): insert statement which needs the stat

        Returns:
            TYPE: Description
        """
        try:
            float(text)
            insert_command += "{}, ".format(text)

        except ValueError:
            insert_command += '"{}", '.format(text)
        return insert_command

    def format_insert_end(insert_command):
        """When finalizing an insertion command:
        the final , and space need to be removed
        and the ); must be added.

        Args:
            insert_command (str): insertion command being completed
        """
        insert_command = insert_command[0:-2]
        insert_command += ");"
        return insert_command

    # used to determine if a bs element is a comment
    def is_comment(element):
        return isinstance(element, Comment)

    def get_soup(url):
        temp_data = requests.get(url)

        with open("temp.html", 'wb') as f:
            f.write(temp_data.content)

        with open("temp.html") as fp:
            soup = BeautifulSoup(fp, features="lxml")
            return soup

    def printProgressBar(iteration, total, prefix='', suffix='',
                         decimals=1, length=100, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in
                percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

    def format_name(name):
        """The sinful &nbsp; is purged with this method.
        Args:
            name (str): name we are purging
        """
        name_formatted = list(name)
        for char in name_formatted:
            if ord(char) == 160:
                name_formatted[name_formatted.index(char)] = " "
        return ''.join(name_formatted)

    def unformat_name(name):
        """
        sinnn.
        """
        name_formatted = list(name)
        for char in name_formatted:
            if char == " ":
                name_formatted[name_formatted.index(char)] = chr(160)
        return ''.join(name_formatted)

    def hamming_distance(str1, str2):
        """Finds just how different two strings are.
        Note that this may be tricky for abbreviated names.
        for instance... matt boyd:
            Matthew Boyd
            Matt Barnes <= matches the wrong one...

        Args:
            str1 (str): first string
            str2 (str): second string
        Returns:
            int: distance between two input strings
        """
        dist = 0
        for i in range(len(str1)):
            try:
                if str1[i] != str2[i]:
                    dist += 1

            except IndexError:
                # when one is shorter than the other... add abs of diff in size
                # to the dist
                dist += abs(len(str1) - len(str2))

        return dist

    def find_player_issue(db, season, player):
        """When there is an issue with matching names due to accents, abbrs,
        or punctuation, this guy comes into play. Finds the player that matches
        the name the closest (hopefully our desired player).
        Args:
            db (db conn): figure it out
            player (str): name of player to match
        """
        # First off, get the players.
        # Format of return is list of tuples where first entry of each
        # tuple is the name.
        players = db.execute_command("""
            SELECT player
            FROM player_info
            WHERE season={};
            """.format(season))

        min_dist, player_match = 10, ''
        for player2 in players:
            dist = Basic_Utils.hamming_distance(player, player2[0])
            if dist < min_dist:
                min_dist = dist
                player_match = player2[0]

        return player_match
