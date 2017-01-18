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
from app_functions import fatal, readPgpass, getPgDBnames, pageNav, getSchemas, getTables

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
#  Metadata Functions
#===========================================================================        

def getPageID():
    if request.args.get('page_id') is not None:
        page_id = request.args.get('page_id')
    elif form.page_id.data is not None:
        page_id = form.page_id.data
    else:
        page_id = 0
    return page_id

def getPageInfo(page_id):
    if page_id > 0:
        psql = "select * from public.page where page_id = %s " % (page_id);
    else:
        psql = "select * from public.page order by page_id";    
    result = conn.execute(psql);
    fetchall = result.fetchall()
    pageInfo = pd.DataFrame(fetchall)
    return pageInfo

def getPageContent(page_id):
    if (page_id is None) or (page_id == 0) :
        fatal("getPageContent function requires a numeric page_id argument > 0")
    csql = "select c.content_id, c.content_md, c.content_ht from public.content c ";
    csql += "join public.page_content pc on c.content_id = pc.content_id ";
    csql += "join public.page p on p.page_id = pc.page_id ";
    csql += "where pc.page_id = %s " % request.args.get('page_id') ;
    result = conn.execute(psql);
    fetchall = result.fetchall()
    pageContent = pd.DataFrame(fetchall)
    return pageContent
    
def postPageContent(page_id, content_id, target):    
    #Get content that has been submitted via the form
    new_content_md = form.content_md.data
    new_content_ht = form.content_ht.data
    if new_content_md is not None:
        if (len(new_content_md.strip()) > 0):
            if (content_id > 0):
                contsql = "update public.content set "
                contsql += "content_md = '%s', content_ht = '%s' where content_id = %s " % (new_content_md, new_content_ht, str(content_id)); 
                #flash(contsql)
                conn.execute(contsql)
            else:
                #flash("Trying to update with " + new_content_md )
                #flash("Also "+ new_content_ht)
                contsql = "insert into public.content (content_md, content_ht) VALUES ";
                contsql += "('%s', '%s')" % (new_content_md, new_content_ht);
                xsql = "insert into public.page_content "
                xsql += "(select %s as page_id, max(content_id) as content_id from public.content) " % str(page_id);
                #flash(contsql)
                #flash(xsql)
                #Note: this is not the most ironclad process. I do the insert on the content table, then do the insert on the 
                #  linking table, using the new content_id that was just created by the insert.   
                conn.execute(contsql)
                conn.execute(xsql)
        #Refresh the page to show the new content
        return redirect(url_for(target, page_id = page_id ))
     
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

        #Pull the page title off the first row (that is the app subtitle). The rest of the rows are passed to the view for parsing.
        page_title = pageresult.fetchone()[2]

        #Find out if you have any results to write back
        if request.method == 'POST':
            new_page_name = form.new_page_name.data
            new_page_title = form.new_page_title.data
            if (len(new_page_name.strip()) > 0):
                newsql = "insert into public.page (page_name, page_title, page_target) Values ('%s', '%s', '%s') ON CONFLICT (page_name) DO UPDATE SET page_title = '%s'" % (new_page_name.strip(), new_page_title.strip(), 'content', new_page_title.strip());  
                conn.execute(newsql)
                #Refresh Page so you can see what you have just done
                return redirect(url_for('index'))


    #No results to write back?  Open the web page !                                                         
    return render_template('index.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           page_title=page_title,
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

        #Page Info
        psql = "select * from public.page where page_id = %s " % request.args.get('page_id') ;

        #The pageresult has one record - corresponding to page_id. Variables are page_id, page_name, page_title, and page_target
        pageresult = conn.execute(psql);
        #Get the paramters out of it
        pageparam = pageresult.fetchone()
        page_id = pageparam[0]
        page_name = pageparam[1]
        page_title = pageparam[2]
        page_target = pageparam[3]

        # Content Info
        csql = "select c.content_id, c.content_md, c.content_ht from public.content c ";
        csql += "join public.page_content pc on c.content_id = pc.content_id ";
        csql += "join public.page p on p.page_id = pc.page_id ";
        csql += "where pc.page_id = %s " % request.args.get('page_id') ;

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
        else:
            content_id = 0
            content_markdown = ''
            content_html = ''
        #flash("Content id for page_id " + str(page_id) + " is "+str(content_id))
        #flash("The actual content is " + content_markdown);

        #Get content that has been submitted via the form
        #Note -- this still just handles one content per form. Somehow the content_id is not being properly passed through the renderer
        new_content_md = form.content_md.data
        new_content_ht = form.content_ht.data
        if new_content_md is not None:
            if (len(new_content_md.strip()) > 0):
                if (content_id > 0):
                    contsql = "update public.content set "
                    contsql += "content_md = '%s', content_ht = '%s' where content_id = %s " % (new_content_md, new_content_ht, str(content_id)); 
                    #flash(contsql)
                    conn.execute(contsql)
                else:
                    #flash("Trying to update with " + new_content_md )
                    #flash("Also "+ new_content_ht)
                    contsql = "insert into public.content (content_md, content_ht) VALUES ";
                    contsql += "('%s', '%s')" % (new_content_md, new_content_ht);
                    xsql = "insert into public.page_content (page_id, content_id) VALUES (%s, %s)" % (str(page_id), '1') 
                    xsql = "insert into public.page_content (select %s as page_id, max(content_id) as content_id from public.content) " % str(page_id);
                    #flash(contsql)
                    #flash(xsql)
                    #Note: this is not the most ironclad process. I do the insert on the content table, then do the insert on the 
                    #  linking table, using the new content_id that was just created by the insert.   
                    conn.execute(contsql)
                    conn.execute(xsql)

            #Refresh the page to show the new content
            return redirect(url_for('content', page_id = page_id ))


    #All done?  Open the web page!                                                         
    return render_template('content.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           page_name=page_name,
                           page_title = page_title,
                           page_target = page_target,
                           pagecontents=pagecontents,
                           content_id = content_id,
                           content_html = content_html,
                           content_markdown = content_markdown,
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

    #Get the page id out of the GET parameters
    if request.args.get('page_id') is None:
        return redirect(url_for('index'))
    else:
        page_id = request.args.get('page_id')

    #Get the detailed page info (name, title, target)
    psql = "select * from public.page where page_id = %s " % page_id ;
    pageresult = conn.execute(psql);
    #Get the paramters out of it
    pageparam = pageresult.fetchone()
    page_name = pageparam[1]
    page_title = pageparam[2]
    page_target = pageparam[3]

    #Get the Page Content
    csql = "select c.content_id, c.content_md, c.content_ht from public.content c ";
    csql += "join public.page_content pc on c.content_id = pc.content_id ";
    csql += "join public.page p on p.page_id = pc.page_id ";
    csql += "where pc.page_id = %s " % str(page_id) ;

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
    else:
        content_id = 0
        content_markdown = ''
        content_html = ''
    #flash("Content id for page_id " + str(page_id) + " is "+str(content_id))
    #flash("The actual content is " + content_markdown);


    #======================================
    #The code for showing Database info
    #======================================
    #Set the session as always logged in, for now                                                                              
    session['logged_in'] = True

    #initialize the variables
    numschema = 0; numdb = 0; note =''; schema_list = ''; allTables = ''; dbname = 'postgres'; 
    allSchemas = ''; allFK = ''; num_allFK = 0; num_tables = '';

    #Get the name of all datbases in the Postgresql instance, connecting using the pg default db                           
    dbnames = getPgDBnames(user)

    #Get Database info the User has selected
    if request.method == 'POST':
        dbname = request.form['database']
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

    #Open the web page with the variables set (found) by the python code                                                   
    return render_template('seemedb.html', 
                           project_name = app_name, 
                           page_id = page_id ,
                           page_name = page_name,
                           page_title = page_title,
                           page_target = page_target,
                           content_id = content_id,
                           content_html = content_html,
                           content_markdown = content_markdown,
                           dbname=dbname, username=user, numschema=numschema,
                           dbnames=dbnames, numdb=numdb, note=note,
                           schema_list = schema_list, allTables = allTables,
                           allSchemas = allSchemas, allFK = allFK, num_allFK = num_allFK,
                           num_tables=num_tables
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


