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
from app_functions import fatal, readPgpass, getPgDBnames, pageNav

import forms
from forms import ContactForm, RegistrationForm, AddPage

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
    #Determine what page has been requested
    if request.args.get('page_title') is None:
        page_title=''; page_name='index';
        url = url_for('index');
        #We want to get the information out of the page table
        #And send it to the page to render
        isql = "select * from public.page";
        dbURL = readPgpass(app_name, user)
        engine = create_engine(dbURL)
        conn = engine.connect()
        pageresult = conn.execute(isql)

    else:
        pageresult = []
        page_title = request.args.get('page_title');
        if request.args.get('page_name') is None:
            page_name = page_title;
        else:
            page_name = request.args.get('page_name')
        url = url_for('index')+"?page_title="+page_title+"&page_name="+page_name;

    #Open the web page                                                         
    return render_template('index.html', 
                           show_link=1,
                           project_name = app_name, 
                           page_name=page_name, 
                           page_title=page_title,
                           url = url, pageresult = pageresult
                           
                           )

@app.route('/add_page', methods=['GET', 'POST'])
def add_page():
    from sqlalchemy import create_engine, engine, exc
    page_name = 'add_page'
    page_title = 'Add Page'
    url = ''
    form = AddPage(request.form)
    if request.method == 'POST':
        new_page_name = form.page_name.data
        new_page_title = form.page_title.data
        flash('You want to add page '+new_page_name+" with title "+new_page_title)
    
        return redirect(url_for('index'))
    if request.method == 'GET':
        new_page_name = request.args.get('new_page_name_1');
        new_page_title = request.args.get('new_page_title_1');
        newsql = "insert into public.page (page_name, page_title) Values ('%s', '%s')" % (new_page_name.strip(), new_page_title.strip());  
        page_title = newsql;
        #make the database connection to PG
        dbURL = readPgpass(app_name, user)
        engine = create_engine(dbURL)
        conn = engine.connect()
        conn.execute(newsql)
    return render_template('add_page.html',
                           form=form,
                           show_link=0,
                           project_name = app_name, 
                           page_name=page_name, 
                           page_title=page_title,
                           url = url
                           )

@app.route('/form_page', methods=['GET', 'POST'])
def form_page():
    #Determine what page has been requested
    page_nav = pageNav(request.args)
    page_name = page_nav[0]
    page_title = page_nav[1]
    url = page_nav[2]

    #form = AddPage(request.form)
    #if request.method == 'POST':
    #    new_page_name = form.page_name.data
    #    new_page_name = form.page_title.data
    #    flash('Want to add page '+new_page_name)
    #
    #    return redirect(url_for('index'))
    return render_template('form_page.html', 
                           show_link=0,
                           project_name = app_name, 
                           page_name=page_name, 
                           page_title=page_title,
                           url = url
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
