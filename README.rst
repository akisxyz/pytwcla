Pytwcla
=======
A Python command-line application for collecting keyword-based Twitter data.

Compatible with Python 2.7 and 3.5.

Installation
------------
Install from `PyPI <https://pypi.python.org/pypi/pytwcla>`_ via `pip <https://pypi.python.org/pypi/pip>`_ :

    pip install pytwcla

Dependencies:

 - `Tweepy <https://github.com/tweepy/tweepy>`_ >= 3.5

Setup
-----
Edit ``api.ini`` with your `Twitter credentials <https://dev.twitter.com/oauth/overview/application-owner-access-tokens>`_ .

> ``pytwcla -h`` will point you to the location where ``api.ini`` has been installed.

Usage
-----
If installation is successful, an executable script should be somewhere in your ``PATH``. Open a command-line and try it out:

    pytwcla

**REST search** (keyword = 'fintech'):

    pytwcla fintech -r

Returns IDs and Dates of Tweets matching the specified keyword and saves them in a SQLite database file named fintech_rest.db.

**Stream search** (keyword = 'fintech'):

    pytwcla fintech -s

Returns IDs and Dates of relevant Tweets and saves them in fintech_stream.db.

**Join** REST and Stream search results:

    pytwcla fintech -j

> Neither the REST nor the Stream search API is meant to be an exhaustive source of Tweets.

**Create csv**:

    pytwcla fintech -c

Creates .csv files with daily keyword counts.

> If fintech_rest.db exists it creates fintech_rest.csv.

License
-------
`MIT <https://opensource.org/licenses/MIT>`_
