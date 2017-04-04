# Simple
This project is a Python/Flask/PostgreSQL project that creates a place to explore and answer "how'd they do that?" questions involving web programming. Every page is about "something", but it is also a sampler of sorts, a compendium of techniques, code, and references that you can use to get the same effects in your own projects. The main idea is to pull together a variety of open source code to simplify setup for any project that involves functions like navigation, visualization, and "try-it" editors.

This application is run with Python, Flask, SQLAlchemy, and PostgreSQL.

It was developed on Mac OS 10.11.6, using Python 2.7.10 (which is natively installed on Mac) and Mac Xcode 8 (available for [download](https://developer.apple.com/xcode/)) for command line tools (primarily git).

To ensure that Flask, SQLAlchemy, and the other required Python modules are installed before running this app, run the following (under ```sudo```):

```
easy_install pip
pip install flask
pip install sqlalchemy
pip install pandas
pip install wtforms
pip install psycopg2

```

The minimum version of PostgreSQL for running this application is 9.5, in which ["upsert"](https://www.postgresql.org/docs/9.5/static/sql-insert.html)  (insert, or on conflict update) is provided. 

This application is currently running on PostgreSQL 9.6.2-2 from [BigSQL](https://www.bigsql.org/postgresql/installers.jsp).  BigSQL was chosen because the install includes pgAdmin3 compatible with later versions of PostgreSQL (9.5 and above). 

Command line interaction with PostgreSQL is done with psql, which is included as part of the PostgreSQL install but has to be set up in your .bash_profile file in order to run it from the command line.

Open the .bash_profile file in your home (~) directory, using the text editor of your choice (I use emacs). 

``` 
emacs ~/.bash_profile
```
The above command will also create the file if it doesn't already exist.

add this line: 
```
export PATH=[path to psql bin]:$PATH
```
where the ```[path to psql]`` is the location of the sql bin on your computer.  For example,

```
export PATH=$PATH:/Users/geekillustrated/PostgreSQL/pg96/bin

```

>If you don't know where your psql has been installed, you can find it on a Mac (or Linux) with 
```
locate psql | grep bin
```

>If you are running ```locate``` for the first time, you may get a prompt that tells you that you have to have to load the locate library before being able to use it.  Follow the screen prompts and wait for it to finish.  It can take quite a while, up to 5 minutes or so. There is no progress bar so be patient and wait until the bash prompt returns.  When it does, re-run the locate command to find the location, and add it to your .bash_profile file as above.

Once you have added psql to the $PATH,  refresh your bash profile:

<code>. ~/.bash_profile </code>

Run psql from your terminal:
```
psql
```

If you get a message like:

```
FATAL: password authentication failed for user "[user]"
```
don't worry, just specify User (note the capital U) postgres:

```
psql -U postgres
```
This will allow you to interact with PostgreSQL as the administrative superuser, which is what you want in this case.

You now have the framework set up to load and run the app, which you can download from [Github](https://github.com/jstofel/Simple).

Once you have downloaded the code from [Simple](https://github.com/jstofel/Simple), download the two database backup files Adventureworks.backup and Simple.backup from [SimpleDB](https://github.com/jstofel/SimpleDB).   Create the two databases on PostgreSQL by first creating each named empty database, then "restoring" from the backup files.

Your code download should produce a directory structure of the form 
```
Simple/
   runserver.py
   Simple/
	__init__.py
	views.py
	forms.py
	app_functions.py
	db_functions.py
	network_functions.py
	static/
		styles.css
		local_scripts.js
		img/	
			*.png
		html/
			*.html
	templates/
		layout.html
		content.html
		....
```
Run the app in the top level of Simple:
python runserver.py

Find the application at localhost:5000.
			