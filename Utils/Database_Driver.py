"""
Handles all of the fun database mumbo jumbo
"""

import sqlite3 as sqlite
import sys
from Utils.Constants import Constants
import pandas as pd


class Database_Driver:

    def __init__(self, db_path):
        self.db_path = db_path

    def execute_insert(self, command):
        """Executes an insert statement.
        Has some nifty error codes to help you debug.

        return 1: Looks like baseball reference added new columns!

        Args:
            command (str): SQLite3 Insertion statement
        """
        try:
            con = sqlite.connect(self.db_path)

            with con:
                cur = con.cursor()
                cur.execute(command)
                con.commit()

        except sqlite.Error as e:

            if con:
                con.rollback

            else:
                print("Error {}".format(e.args[0]))
                print("Here is the offending command: ")
                print(command)
                sys.exit()

    def execute_select(self, command):
        try:
            con = sqlite.connect(self.db_path)

            with con:

                cur = con.cursor()
                cur.execute(command)

                return cur.fetchall()

        except sqlite.Error as e:

            if con:
                con.rollback

            print("Error {}".format(e.args[0]))
            print("Here is the offending command: ")
            print(command)
            sys.exit(1)

    def execute_command(self, command):
        """
            runs a command and returns the results.
        """
        try:
            con = sqlite.connect(self.db_path)

            with con:
                cur = con.cursor()
                cur.execute(command)
                con.commit()
                result = cur.fetchall()
                return result

        except (sqlite.Error, sqlite.Warning) as e:
            if con:
                con.rollback

            print("Error {}".format(e.args[0]))
            print("Here is the offending command: ")
            print(command)
            sys.exit(1)

    def select_to_df(self, command):
        """Executes sqlite command and returns result
        as a df.
        Args:
            command (string): sqlite3 command to be executed.

        Returns:
            df: Pandas df with info we pulled.
        """
        try:
            con = sqlite.connect(self.db_path)
            # with scope closes con when we return
            with con:
                df = pd.read_sql_query(command, con)
                return df

        except (sqlite.Error, sqlite.Warning) as e:
            if con:
                con.rollback

            print("Error {}".format(e.args[0]))
            print("Here is the offending command: ")
            print(command)
            sys.exit(1)
