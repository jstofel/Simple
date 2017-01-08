from Simple import app

#===========================================================================        
##Import Python Modules Used in App
#===========================================================================        
import os, sys, getpass
from flask import Flask, redirect, url_for, request, session, g,  abort, render_template, flash

from sqlalchemy import create_engine, schema, engine, exc
from sqlalchemy.engine import reflection

import pandas as pd

#===========================================================================        
##Set project level variables
#===========================================================================        
project_name = os.getcwd().split('/')[-1]
user = getpass.getuser()
dbName = project_name
dbName= 'GeekIllustratedDOM'

#===========================================================================        
##Define deg=bugging functions
#===========================================================================        
def fatal(*L):
     print >>sys.stderr, ''.join(L)
     raise SystemExit
#===========================================================================        
##Connect to application metadata database
#===========================================================================        
protocol = 'postgresql'
URL_FORMAT = "%s://%s:%s@%s/%s"
fname = "/Users/"+user+"/.pgpass"
f = open(fname, 'rb')
for a in f.readlines():
  host, port, database, username, password = a.rstrip().split(':')
  if (database == dbName):
      engineURL = URL_FORMAT % (protocol, username, password, host, database)
  elif (database == '*'):
      engineURL = URL_FORMAT % (protocol, username, password, host, dbName)
  else:
      engineURL = ''
try:
   engine = create_engine(engineURL)
   meta = engine.connect()
except exc.SQLAlchemyError as detail:
   print(engineURL)
   fatal("Could not query : %s" % detail)

#===========================================================================        
##Define the Functions that Render the Views (HTML pages)                                                
#===========================================================================        
#Define the home (index) page with a single slash, and define the page as a render function 
@app.route('/', methods=['GET', 'POST'])
def index():
    page_name='index'; 
    if request.args.get('page_title') is None:
        page_title='';
        url = url_for('index');
    else:
        page_title = request.args.get('page_title');
        url = url_for('index')+"?page_title="+page_title;
    #Open the web page                                                         
    return render_template('index.html', 
                           project_name = project_name, page_name=page_name, 
                           page_title=page_title,
                           url = url, basename=project_name
                           )

