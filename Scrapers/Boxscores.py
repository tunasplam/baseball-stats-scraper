from Utils.Basic_Utils import Basic_Utils as BU
from Utils.Constants import Constants
from bs4 import BeautifulSoup, Comment
import re


"""
TODO This turned into a monster split off the play by plays maybe
"""


class Boxscores:

    def __init__(self, db, season, batting_stats, pitching_stats):
        self.db = db
        self.season = season
        # the objects for the classes that grab batting and pitching
        # stats already instantiated in main method.
        self.batting_stats = batting_stats
        self.pitching_stats = pitching_stats

    # TODO this method may no longer be needed.
    def boxscores(self, team):
        """Get's the team's pitching and batting boxscores for the entire
           season.
        Populates both these tables:
            boxscores_batting_{team}
            boxscores_pitching_{team}
        """

        url = "https://www.baseball-reference.com/teams/" + team + "/" \
            + str(self.season) + "-schedule-scores.shtml"

        schedule_soup = BU.get_soup(url)
        tbody = schedule_soup.find_all('tbody')
        games = tbody[0].find_all('tr')

        for game in games:
            # th has the game num. See if we need to skip.
            game_num_tag = game.find('th')
            if "aria-label" in str(game_num_tag):
                continue

            boxscore_link = Constants.URL_ROOT + \
                game.find('td', {'data-stat': "boxscore"}).find('a')['href']

            self.handle_game(boxscore_link, team, game_num_tag.text)

            # TODO adjust for covid season!
            BU.printProgressBar(int(game_num_tag.text), 162,
                                prefix="{} Boxscores".format(team),
                                length=30)

    def handle_game(self, url, team, game_num):
        """    parent function gets link to boxscore, this handles it all.
        Args:
            url (str): url to game page
            team (str): team name code
            game_num (int): season game number for team
        """

        game_soup = BU.get_soup(url)

        # table code is commented out... get the comments.
        comments = game_soup.find_all(
            string=lambda text: isinstance(text, Comment))
        for comment in comments:

            # Will get us two tables,
            # first is the batting and second is the pitching.
            if "{} Table".format(Constants.teamInfo[team]['full name']) in comment:

                if "batting" in comment:
                    self.batting_stats.boxscores_batting(
                        BeautifulSoup(comment, features="lxml"),
                        team, game_num)

                elif "pitching" in comment:
                    self.pitching_stats.boxscores_pitching(
                        BeautifulSoup(comment, features="lxml"),
                        team, game_num)

            elif "Play by Play Table" in comment:
                boxscore_link = re.findall(r'\/boxes.*', url)[0]

                # play by play
                # check if the game already entered.
                results = self.db.execute_command("""
                    SELECT *
                    FROM play_by_play
                    WHERE boxscore_link = "{}";
                    """.format(boxscore_link))

                if len(results) == 0:
                    self.get_play_by_play(
                        BeautifulSoup(
                            comment, features="lxml"), team, boxscore_link)

        self.get_innings_runs_summary(game_soup, team, game_num)

    def get_play_by_play(self, boxscore_soup, team, boxscore_link):
        """Get the play by play events for the boxscore.
        later on needs to be populated with the player links for the opposing
        teams. this is done in update_play_by_play and takes A LONG time.

        Args:
            boxscore_soup (bs4): table tag for the play by play.
            team (str): team we are pulling data for
            boxscore_link (str): end of url for boxscore_link.
                                 used as part of key.
        """
        # all the events have id="event_{num}" and class="{top/bottom}_inning"
        event_tags = boxscore_soup.find_all('tr', class_="top_inning")
        event_tags += boxscore_soup.find_all('tr', class_="bottom_inning")

        # code for the opposing team.. .
        team_tags = boxscore_soup.find_all('td',
                                           attrs={'data-stat':
                                                  'batting_team_id'})
        opp_team = ""
        for tag in team_tags:
            if len(tag.text) > 0 and tag.text != team:
                opp_team = tag.text
                break

        for tag in event_tags:
            insert_command = """
            INSERT INTO play_by_play
            VALUES({}, "{}", """.format(self.season, boxscore_link)

            td_tags = tag.find_all('td')

            # inning is in th tag
            insert_command += '"{}", '.format(tag.find('th').text)

            batting_team = ""
            for td_tag in td_tags:

                # used for pulling pitcher and batter links below...
                if "batting_team_id" in str(td_tag):
                    if td_tag.text == team:
                        batting_team = team
                    else:
                        batting_team = opp_team

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
                        pitch_sequence_str = re.findall(r'(?<=\w).*?(?=$)',
                                                        td_tag.text)[0]
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

                # pitcher and batter... formatting to kill nbsp
                elif "batter" in str(td_tag) or "pitcher" in str(td_tag):
                    # awful crap here but I want to go to bed.
                    temp_team = ""
                    if batting_team == team and "batter" in str(td_tag):
                        temp_team = team

                    elif batting_team == opp_team and "batter" in str(td_tag):
                        temp_team = opp_team

                    if batting_team == team and "pitcher" in str(td_tag):
                        temp_team = opp_team

                    elif batting_team == opp_team and "pitcher" in str(td_tag):
                        temp_team = team

                    name = BU.format_name(td_tag.text)
                    # add the batter's name
                    insert_command += '"{}", '.format(name)
                    # get the link to his player page.
                    player_page_link = self.db.execute_command("""
                        SELECT player_link
                        FROM player_info
                        WHERE season={} AND team="{}" AND player="{}";
                    """.format(self.season, temp_team, name))
                    try:
                        insert_command += '"{}", '.format(player_page_link[0][0])
                    except IndexError:
                        # players with weird things going on like accents
                        # abbreviations or hyphens.
                        issue_name = BU.find_player_issue(
                            self.db, self.season, name)
                        player_page_link = self.db.execute_command("""
                            SELECT player_link
                            FROM player_info
                            WHERE season={} AND team="{}" AND player="{}";
                        """.format(self.season, temp_team, issue_name))
                        insert_command += '"{}", '.format(player_page_link)

                else:
                    insert_command = BU.append_stat_to_statement(
                        td_tag.text, insert_command)

            insert_command = BU.format_insert_end(insert_command)
            self.db.execute_insert(insert_command)

    def get_innings_runs_summary(self, boxscore_soup, team, game_num):
        """Takes the boxscore page and grabs the runs per inning and R/H/E
        totals for the game and puts them in the db.

        Args:
            boxscore_soup (bs4): Soup of our boxscore page for the game.
            team (str): Team we are adding info for.
            game_num (int): Number game for the team we are grabbing info for.
        """

        # first half of nums is the away team, second half home team.
        # TODO due to rescheduling and playing somewhere else for things
        # like riots or hurricanes, we need to base the home and away
        # off of the configuration of the boxscore (home team on bottom)
        # i.e. game 23 of TBR 2015 was in TB but BAL was home team.
        # we can look at the src for the logo image on the boxscores.
        # TODO above was an old TODO, was it fixed?
        home_or_vs = ""
        image_tags = boxscore_soup.find_all("div", attrs={
            "class", "media-item logo loader"})
        # 3rd occurance is away team, 4th is home team.
        if team in image_tags[3].find("img")['src']:
            home_or_vs = ""
        else:
            home_or_vs = "@"

        # the innings boxes are all td tags with class="center"
        tags = boxscore_soup.find_all('td', class_="center")

        nums = self.extract_nums(tags)

        # need to know if home or away...
        # first half of nums is the away team, second half home team.
        if home_or_vs == "@":
            # away team.
            self.populate_innings_runs_summary(
                nums[0:len(nums)//2], team, game_num, "team", image_tags)

            # home team
            self.populate_innings_runs_summary(
                nums[len(nums)//2:len(nums)],
                team, game_num, "opp", image_tags)
        else:
             # away team.
            self.populate_innings_runs_summary(
                nums[0:len(nums)//2], team, game_num, "opp", image_tags)

            # home team
            self.populate_innings_runs_summary(
                nums[len(nums)//2:len(nums)],
                team, game_num, "team", image_tags)

    def extract_nums(self, tags):
        """Takes the soup for the boxscore page, finds all the td tags
        That contain relevant info, and sticks all the numbers in an
        ordered list.
        Args:
            tags (list bs4 tags): td tags that may or may not contain info
        Return:
            nums (list): numbers of runs scores and totals. X for
            irrelevant 9th innings.

        """
        # Only want the tags with integer strings or X. X -> NULL.
        # we add later bc we need to count the number of elements
        # in the list to determine if we have extra innings.
        nums = []
        for tag in tags:
            try:
                nums.append(int(tag.text))
            except ValueError:
                if tag.text == 'X':
                    nums.append('X')
        return nums

    def populate_innings_runs_summary(
            self, nums, team, game_num, side, image_tags):
        """Spaghetti that updates that schedules games with the runs per
        inning summary stats.

        Args:
            nums (list): All the innings and totals info
            team (str): Team whose boxscore we are updating
            game_num (int): Game num of the season for team.
            side (str): "team" if team "opp" if opp.
        """
        # flags to keep track of where we are in
        # the ordered list
        inning = 1
        extras, additional_innings = False, 0
        extras_runs = 0

        # regular 9-inning games will create lists with 12 nums
        if len(nums) > 12:
            extras = True
            additional_innings = (len(nums) - 12)//2

        for num in nums:
            # normal inning
            if inning <= 9:

                if num == 'X':
                    num = "NULL"

                update_command = """
                UPDATE schedules
                SET {}{} = {}
                WHERE team="{}" AND season={} AND game_num={}
                """.format(side, inning, num, team, self.season, game_num)
                self.db.execute_command(update_command)

                inning += 1

        # now for more than 9th check if extra innings...
        if extras:
            # yeah, should have thought of this before.
            extras_runs = sum(nums[9:-3])

        # Check if weird reschedule situation... if image_tags[2] ==
        # image_tags[3] then we got weird situation as described above.
        riot_fix = False
        if (team in image_tags[3].find("img")['src'] and
            team in image_tags[0].find("img")['src']) or (
                team in image_tags[1].find("img")['src'] and
                team in image_tags[2].find("img")['src']):
            riot_fix = True

        riot_fix_cmd = """
        UPDATE schedules
        SET home_team_actually_away = "{}"
        WHERE season={} AND team="{}" AND game_num={}
        """.format(riot_fix, self.season, team, game_num)
        self.db.execute_command(riot_fix_cmd)

        # for totals.. just do last two elements in list.
        update_command = """
        UPDATE schedules
        SET {}_H = {}
        WHERE team="{}" AND season={} AND game_num={}
        """.format(side, nums[-2], team, self.season, game_num)
        self.db.execute_command(update_command)

        update_command = """
        UPDATE schedules
        SET {}_E = {}
        WHERE team="{}" AND season={} AND game_num={}
        """.format(side, nums[-1], team, self.season, game_num)
        self.db.execute_command(update_command)

        if extras:
            # update extras_runs_teams and extras_runs_opp
            update_command = """
            UPDATE schedules
            SET {}_extras={}
            WHERE team="{}" AND season={} AND game_num={}
            """.format(side, extras_runs, team, self.season, game_num)
        else:
            # No extra innings? NULL!
            update_command = """
            UPDATE schedules
            SET {}_extras=NULL
            WHERE team="{}" AND season={} AND game_num={}
            """.format(side, team, self.season, game_num)
        self.db.execute_command(update_command)

        # column for additional innings.
        update_command = """
        UPDATE schedules
        SET additional_innings={}
        WHERE team="{}" AND season={} AND game_num={}
        """.format(additional_innings, team, self.season, game_num)
        self.db.execute_command(update_command)

    def update_play_by_play(self):
        """Call at the very end. Go through all the play by plays and update
           missing entries. This takes a long time as there are about 100k ABs
           per season.
        """
        play_by_plays = self.db.execute_command("""
            SELECT *
            FROM play_by_play
            WHERE season={};
        """.format(self.season))
        i = 0
        for entry in play_by_plays:
            # batter needs updating.
            if entry[12] == '[]':
                try:
                    batter_link = self.db.execute_command("""
                        SELECT player_link
                        FROM player_info
                        WHERE player="{}";
                    """.format(entry[11]))[0][0]

                # if getting to here then likely an accent or abbreviation
                # is a problem.
                # TODO: ISSUES? Could be possible here for abbreviated names.
                except IndexError:
                    batter_link = self.db.execute_command("""
                        SELECT player_link
                        FROM player_info
                        WHERE player="{}";
                    """.format(BU.find_player_issue(
                        self.db, self.season, entry[11])))[0][0]

                update_command = """
                    UPDATE play_by_play
                    SET link_to_batter="{}"
                    WHERE batter="{}";
                """.format(batter_link, entry[11])
                self.db.execute_command(update_command)

            # pitcher needs updating.
            elif entry[14] == '[]':
                try:
                    pitcher_link = self.db.execute_command("""
                        SELECT player_link
                        FROM player_info
                        WHERE player="{}";
                        """.format(entry[13]))[0][0]

                except IndexError:
                    pitcher_link = self.db.execute_command("""
                        SELECT player_link
                        FROM player_info
                        WHERE player="{}";
                        """.format(BU.find_player_issue(
                                   self.db, self.season, entry[13])))[0][0]

                update_command = """
                UPDATE play_by_play
                SET link_to_pitcher="{}"
                WHERE pitcher="{}";
                """.format(pitcher_link, entry[13])
                self.db.execute_command(update_command)

            i += 1
            BU.printProgressBar(i, len(play_by_plays),
                                prefix="Fixing play_by_plays",
                                decimals=3, length=50)
