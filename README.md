# baseball-stats-scraper
My scraper to get a whole season's worth of information from Baseball Reference with the press of a button (and a lot of patience)

# Description

This program scrapes a bunch of tables on baseball reference and stores them in an sqlite3 db. It pulls a lot of stats and takes a long time to run, but it works.

# Installing

Requires python, SQLite3, and Beautiful Soup 4. I have only run this on Linux so I am not sure if it will work on Windows but you're welcome to try if you wish. Download this folder somewhere and run the program.

# Executing

For now, you have to run 
```
python table_creator.py
```
first in order to set up the tables. But soon I will add a cli for the downloader that allows you to just run everything from Main.py.

After table_creator.py is run, you need to set the season variable in Main.py (again, something that I will change very soon once I had a cli). Oh, and you also need a few hours. This will take a looonnngg time.

Once the program has run its course, you will find baseball.db in the same directory (again, once I add a cli, I will add an option to do a custom db location).

# Something happened and the program got interrupted before it could finish!
Thats okay, run it again and it will pick up where it left off.

# What data does it grab?
Check table_creator.py for the schema. Maybe one day I will put together a big list of the tables and the stats and the explanation of what each stat means but... that would be... a lot of work. One day.

# Author
Jordan Porter
