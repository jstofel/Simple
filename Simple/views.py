from Simple import app

#===========================================================================        
##Import Python Modules Used in App
#===========================================================================        
import os, sys, getpass
from flask import Flask, redirect, url_for, request, session, g,  abort, render_template, flash

from sqlalchemy import create_engine, schema, engine, exc
from sqlalchemy.engine import reflection

import pandas as pd

#==========================================================================
##Import Python Functions Specific to this Application
##These functions are in a separate file for both readability and portability
#==========================================================================
import app_functions
from app_functions import fatal, readPgpass, getPgDBnames

#===========================================================================        
##Set Application-Level Static Variables Defined When the Server is Started
#===========================================================================        
app_name = os.getcwd().split('/')[-1]
user = getpass.getuser()
dbName = app_name

#===========================================================================        
##Define the Functions that Render the Views (HTML pages) 
#===========================================================================        
#Define the home (index) page with a single slash, and define the page as a render function 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.args.get('page_title') is None:
        page_title=''; page_name='index';
        url = url_for('index');
    else:
        page_title = request.args.get('page_title');
        if request.args.get('page_name') is None:
            page_name = page_title;
        else:
            page_name = request.args.get('page_name')
        url = url_for('index')+"?page_title="+page_title+"&page_name="+page_name;

    #Open the web page                                                         
    return render_template('index.html', 
                           project_name = app_name, 
                           page_name=page_name, 
                           page_title=page_title,
                           url = url
                           )

