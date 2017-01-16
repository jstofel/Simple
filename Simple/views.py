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
    #Determine if a page has been requested
    if request.args.get('page_id') is not None:
        return redirect(url_for('index', page_id=request.args.get('page_id')))
    else:
        #Define the WTF form used
        form = AddPage(request.form)

        #Initialize parameters
        page_id = 0;

        #Connect to app database so you can get information on pages and content (pageresult and contentresult) out of the database
        #Note: results from query is SQLalchemy ResultProxy object that needs specific methods to access data: read the manual...
        dbURL = readPgpass(app_name, user)
        engine = create_engine(dbURL)
        conn = engine.connect()
        psql = "select * from public.page order by page_id";
        pageresult = conn.execute(psql);

        #Find out if you have any results to write back
        if request.method == 'POST':
            new_page_name = form.new_page_name.data
            new_page_title = form.new_page_title.data
            if (len(new_page_name.strip()) > 0):
                newsql = "insert into public.page (page_name, page_title) Values ('%s', '%s')" % (new_page_name.strip(), new_page_title.strip());  
                conn.execute(newsql)
                #return redirect(url_for('index'))


    #All done?  Open the web page!                                                         
    return render_template('index.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageresult = pageresult,
                           form=form
                           )



#Define the content page 
@app.route('/content', methods=['GET', 'POST'])
def content():
    #Determine if a page has been requested
    if request.args.get('page_id') is None:
        return redirect(url_for('index'))
    else:
        #Connect to app database
        dbURL = readPgpass(app_name, user)
        engine = create_engine(dbURL)
        conn = engine.connect()
        #Initialize parameters
        content_markdown = ''; content_html = ''; page_id = 0; content_id = 0;

        #Define the WTF form used
        form = UpdateContent(request.form)

        #Get what is in the database
        psql = "select * from public.page where page_id = %s " % request.args.get('page_id') ;
        csql = "select c.content_id, c.content_md, c.content_ht from public.content c ";
        csql += "join public.page_content pc on c.content_id = pc.content_id ";
        csql += "join public.page p on p.page_id = pc.page_id ";
        csql += "where pc.page_id = %s " % request.args.get('page_id') ;

        pageresult = conn.execute(psql);
        contentresult = conn.execute(csql);

        if contentresult.rowcount > 0 :
            resultlist = contentresult.fetchone()
            content_id = resultlist[0];
            content_markdown = resultlist[1];
            content_html = resultlist[2];

        #Get any data that has been submitted in the form
        content_id = form.content_id.data
        new_content_md = form.content_md.data
        new_content_ht = form.content_ht.data
        if new_content_ht is not None:
            if len(new_content_ht.strip() > 0):
                if (content_id > 0):
                    contsql = "update public.content set content_md = '%s', content_ht = '%s' where content_id = %s " % (new_content_md, new_content_ht, content_id); 
                else:
                    contsql = "insert into public.content (content_md, content_ht) VALUES ";
                    contsql += "('%s', '%s')" % (conent_md, content_ht);
            conn.execute(contsql)
            #return redirect(url_for('index')?page_id=page_id)


    #All done?  Open the web page!                                                         
    return render_template('content.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageresult=pageresult,
                           content_id = content_id,
                           content_html = content_html,
                           content_markdown = content_markdown,
                           form=form
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
    if request.args.get('new_page_name_1') is not None:
        new_page_name = request.args.get('new_page_name_1');
        new_page_title = request.args.get('new_page_title_1');
        newsql = "insert into public.page (page_name, page_title) Values ('%s', '%s')" % (new_page_name.strip(), new_page_title.strip());  
        page_title = newsql;
        #make the database connection to PG
        dbURL = readPgpass(app_name, user)
        engine = create_engine(dbURL)
        conn = engine.connect()
        conn.execute(newsql)

    isql = "select * from public.page where page_title = '%s' " % 'Add Page' ;
    page_title = 'Add Page' ;
    #Get the information out of the page table
    #And send it to the page to render
    dbURL = readPgpass(app_name, user)
    engine = create_engine(dbURL)
    conn = engine.connect()
    pageresult = conn.execute(isql)

    return render_template('add_page.html',
                           form=form,
                           show_link=0,
                           project_name = app_name, 
                           page_name=page_name, 
                           page_title=page_title,
                           url = url,
                           pageresult = pageresult
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
