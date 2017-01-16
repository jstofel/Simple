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
                newsql = "insert into public.page (page_name, page_title) Values ('%s', '%s') ON CONFLICT (page_name) DO UPDATE SET page_title = '%s'" % (new_page_name.strip(), new_page_title.strip(), new_page_title.strip());  
                conn.execute(newsql)
                #Refresh Page so you can see what you have just done
                return redirect(url_for('index'))


    #No results to write back?  Open the web page !                                                         
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
        page_id = request.args.get('page_id')
        content_markdown = ''; content_html = ''; content_id = 0;

        #Define the WTF form used
        form = UpdateContent(request.form)

        #Get what is in the database
        psql = "select * from public.page where page_id = %s " % request.args.get('page_id') ;
        csql = "select c.content_id, c.content_md, c.content_ht from public.content c ";
        csql += "join public.page_content pc on c.content_id = pc.content_id ";
        csql += "join public.page p on p.page_id = pc.page_id ";
        csql += "where pc.page_id = %s " % request.args.get('page_id') ;

        #The pageresult has one record - corresponding to page_id
        pageresult = conn.execute(psql);
        #The contentresult has 0 or more records, depending on how many content sections
        #    we have added.  The contentresult (like all ResultProxies) are cursor objects,
        #    and right now I only know how to access and discard each row! (ie, not like a
        #    dataframe or data table object that persists and can be repeatedly accessed

        #This should get all results, even empty ones, and put them in a dataframe
        contentresult = conn.execute(csql);
        fetchall = contentresult.fetchall()
        pagecontents = pd.DataFrame(fetchall)

        #This gets just the first row of non-empty results
        contentresult = conn.execute(csql);
        if contentresult.rowcount > 0 :
            resultlist = contentresult.fetchone()
            content_id = resultlist[0];
            content_markdown = resultlist[1];
            content_html = resultlist[2];

            #flash("Content id for page_id" + str(page_id) + " is "+str(content_id))

        #Get content that has been submitted via the form
        #Note -- this still just handles one content per form. Somehow the content_id is not being properly passed through the renderer
        new_content_md = form.content_md.data
        new_content_ht = form.content_ht.data
        if new_content_md is not None:
            if (len(new_content_md.strip()) > 0):
                if (content_id > 0):
                    contsql = "update public.content set content_md = '%s', content_ht = '%s' where content_id = %s " % (new_content_md, new_content_ht, content_id); 
                else:
                    contsql = "insert into public.content (content_md, content_ht) VALUES ";
                    contsql += "('%s', '%s')" % (content_md, content_ht);

            #Show what you are trying to do
            #flash(contsql)

            #Do it
            conn.execute(contsql)

            #Refresh the page to show the new content
            return redirect(url_for('content', page_id = page_id ))


    #All done?  Open the web page!                                                         
    return render_template('content.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageresult=pageresult,
                           pagecontents=pagecontents,
                           content_id = content_id,
                           content_html = content_html,
                           content_markdown = content_markdown,
                           form=form
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
