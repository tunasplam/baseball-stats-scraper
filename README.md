# baseball-stats-scraper
My scraper to get a whole season's worth of information from Baseball Reference with the press of a button (and a lot of patience)

# Description

This program scrapes a bunch of tables on baseball reference and stores them in an sqlite3 db. It pulls a lot of stats and takes a long time to run, but it works.

# Installing

Requires python, SQLite3, and Beautiful Soup 4. I have only run this on Linux so I am not sure if it will work on Windows but you're welcome to try if you wish. Download this folder somewhere and run the program.

# Executing

Here is the output of:

```
python Main.py -h
```

usage: Main.py [-h] [-S S] [-o [O]] [-N]

Acquire some baseball data.

options:
  -h, --help  show this help message and exit
  -S S        Seaon to scrape. Use YYYY.
  -o [O]      Name that you want the db to have. Defaults to baseball.db
  -N          If this is present then a new DB will be made. Any db with the same
              name as -o arg will have a backup made of it.

Let it run for a few hours

## Something happened and the program got interrupted before it could finish!
Thats okay, run it again and it will pick up where it left off.

## What data does it grab?
Check table_creator.py for the schema. Maybe one day I will put together a big list of the tables and the stats and the explanation of what each stat means but... that would be... a lot of work. One day.

# Author
Jordan Porter
