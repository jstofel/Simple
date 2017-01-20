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
##Import Python Functions and Forms Specific to this Application
##These functions and forms are in separate files for readability and portability
#==========================================================================

import app_functions
from app_functions import getPageID, getPageInfo, getPageContent, postPageContent

import db_functions
from db_functions import fatal, readPgpass, getPgDBnames, pageNav, getSchemas, getTables, getTableNetwork

import forms
from forms import ContactForm, RegistrationForm, AddPage, UpdateContent

#===========================================================================        
##Set Application-Level Static Variables Defined When the Server is Started
#===========================================================================        
app_name = os.getcwd().split('/')[-1]
user = getpass.getuser()
dbName = app_name

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#===========================================================================        
##Define the Functions that Render the Views (HTML pages) 
#===========================================================================        
#Define the home (index) page with a single slash, and define the page as a render function 
@app.route('/', methods=['GET', 'POST'])
def index():
        #Define the form used on the page
        form = AddPage(request.form)

        #Get Page Id
        page_id = getPageID(form, request)

        #Connect to app database for information on pages and content out of the database
        dbURL = readPgpass(app_name, user)
        engine = create_engine(dbURL)
        conn = engine.connect()

        #=======Get the Page Info as a DataFrame
        pageInfo = getPageInfo(page_id, conn)

        #=============================================
        #Find out if you have any results to write backk
        if request.method == 'POST':
            new_page_name = form.new_page_name.data
            new_page_title = form.new_page_title.data
            if (len(new_page_name.strip()) > 0):
                newsql = "insert into public.page (page_name, page_title, page_target)";
                newsql += "Values ('%s', '%s', '%s') ON CONFLICT (page_name) DO UPDATE SET page_title = '%s'" % (new_page_name.strip(), new_page_title.strip(), 'content', new_page_title.strip());  
                conn.execute(newsql)
                #Refresh Page so you can see what you have just done
                return redirect(url_for('index'))
        #==============

    #No results to write back?  Open the web page !                                                         
        return render_template('index.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageInfo = pageInfo,
                           form=form
                           )

#Define the content page 
@app.route('/content', methods=['GET', 'POST'])
def content():
   #Define the WTF form used
   form = UpdateContent(request.form)

   #Get Page Id
   page_id = getPageID(form, request)

   #Connect to app database for information on pages and content out of the database
   dbURL = readPgpass(app_name, user)
   engine = create_engine(dbURL)
   conn = engine.connect()

   #Determine if a page has been requested
   if request.args.get('page_id') is None:
       return redirect(url_for('index'))
   else:
        #=======Get the Page Info as a DataFrame
        pageInfo = getPageInfo(page_id, conn)

        #======Get Page Contents (Text) as DataFrame
        pageContent = getPageContent(page_id, conn)

        #====Get content that has been submitted via the form and post it
        didPost = postPageContent(page_id, form, conn)
        if (didPost):
            return redirect(url_for(form.page_target.data, page_id = page_id ))

   #All done?  Open the web page!                                                         
   return render_template('content.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageInfo=pageInfo,
                           pageContent = pageContent,
                           dbname='',
                           form=form
                           )

#==================================================
#Define the SeeMeDB page                                                                                                  
#=================================================
@app.route('/seemedb', methods=['GET', 'POST'])
def seemedb():

    #=========================================
    #== The code for getting the App Metadata
    #=========================================

    #Connect to app database
    dbURL = readPgpass(app_name, user)
    engine = create_engine(dbURL)
    conn = engine.connect()

    #Define the WTF form used
    form = UpdateContent(request.form)

    #Get the page id
    page_id = getPageID(form, request)

    #Get the dbname - selected by user or default
    if request.args.get('database') is not None:
        dbname = request.args.get('database')
    elif form.database.data is not None:
        dbname = form.database.data
    else:
        dbname = 'postgres'


    #=======Get Page Info as DataFrame
    pageInfo = getPageInfo(page_id, conn)

    #======Get Page Contents (Text) as DataFrame
    pageContent = getPageContent(page_id, conn)

    #====Get content that has been submitted via the form and post it
    didPost = postPageContent(page_id, form, conn)
    if (didPost):
        return redirect(url_for(form.page_target.data, page_id = page_id, database=dbname ))

    #======================================
    #The code for showing Database info
    #======================================
    #Set the session as always logged in, for now                                                                              
    session['logged_in'] = True

    #initialize the variables
    numschema = 0; numdb = 0; note =''; schema_list = ''; allTables = '';
    allSchemas = ''; allFK = ''; num_allFK = 0; num_tables = ''; link_list = [];

    #Get the name of all datbases in the Postgresql instance, connecting using the pg default db                           
    dbnames = getPgDBnames(user)

    #Get Database info the User has selected
    if dbname != 'postgres':
        schema_list = getSchemas(dbname, user)
        numschema = len(schema_list)

    #Get data frame of all tables by schema                                                                                
    if (numschema > 0):
        returnList = getTables(dbname, user)
        allTables = returnList[0]
        allSchemas = returnList[1]
        allFK = returnList[2]
        num_tables = len(allTables)
        numschema = len(allSchemas)
        num_allFK = len(allFK)

    #Get Network Data Structure
    tableDF = getTableNetwork(dbname, user)

    #Open the web page with the variables set (found) by the python code                                                   
    return render_template('seemedb.html', 
                           project_name = app_name, 
                           page_id = page_id ,
                           pageInfo = pageInfo,
                           pageContent=pageContent,
                           dbname=dbname, 
                           username=user, numschema=numschema,
                           dbnames=dbnames, numdb=numdb, note=note,
                           schema_list = schema_list, allTables = allTables,
                           allSchemas = allSchemas, allFK = allFK, num_allFK = num_allFK,
                           num_tables=num_tables,
			   link_list = link_list,
			   tableDF = tableDF
                           )


@app.route('/register', methods=['GET', 'POST'])
def register():
    #Determine what page has been requested
    page_nav = pageNav(request.args)
    page_name = page_nav[0]
    page_title = page_nav[1]
    url = page_nav[2]

    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        #username = User(form.username.data, form.email.data,
        #            form.password.data)
        username = form.username.data
        #db_session.add(username)
        flash('Thanks for registering '+username)
        return redirect(url_for('index'))
    return render_template('register.html',
                           show_link=0, 
                           form=form,
                           project_name = app_name, 
                           page_name=page_name, 
                           page_title=page_title,
                           url = url
                           )



#=================================================================================                                                                                                   
#Define the logout page                                                                                                                                                              
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


