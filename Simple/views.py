from Simple import app

#===========================================================================        
##Import Python Modules Used in App
#===========================================================================        
import os, sys, getpass
from flask import Flask, redirect, url_for, request, session, g,  abort, render_template, flash, jsonify

from sqlalchemy import create_engine, schema, engine, exc
from sqlalchemy.engine import reflection

import pandas as pd

import json

#==========================================================================
##Import Python Functions and Forms SPECIFIC TO THIS APPLICATION
##These functions and forms are in separate files for readability and portability
## see app_functions.py, db_functions.py, and forms.py in the top level folder
#==========================================================================

import app_functions
from app_functions import getPageID, pageNav, getPageInfo, getPageContent, getPageCode, postPageContent, postJSCode

import db_functions
from db_functions import fatal, readPgpass, getPgDBnames, getSchemas, getTables, getTableNetwork

import network_functions
from network_functions import createNetworkFromDB

import forms
from forms import ContactForm, RegistrationForm, AddPage, UpdateContent, UpdateJSCode, DelPage

#===========================================================================        
##Set Application-Level Static Variables Defined When the Server is Started
#===========================================================================        
app_name = os.getcwd().split('/')[-1]
user = getpass.getuser()
dbName = app_name

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#===========================================================================        
##Set Application-Level Parsers
#===========================================================================        
app.config['DEFAULT_PARSERS'] = [
    'flask.ext.api.parsers.JSONParser',
    'flask.ext.api.parsers.URLEncodedParser',
    'flask.ext.api.parsers.MultiPartParser'
]



#===========================================================================        
##Define the Functions that Render the Views (HTML pages) 
#===========================================================================        
#Define the home (index) page with a single slash, and define the page as a render function 
#Note: this just redirects to the 'first' content page
#But, to allow re-ordering of pages, you will want to change this from page_id to page_order...

@app.route('/', methods=['GET', 'POST'])
def index():
	#Get the page_id from the first page
	osql = "select page_id from page where page_order = 1"
	p = 0
        #Connect to app database 
	dbURL = readPgpass(app_name, user)
	engine = create_engine(dbURL)
	conn = engine.connect()
	page_result = conn.execute(osql)
	for r in page_result:
		p = r[0]
        return redirect(url_for('content', page_id = p ))
                           
#Define the delete page - delete a page with no content
@app.route('/del_page', methods=['POST'])
def del_page():
        #Define the form used on the page
        form = DelPage(request.form)

        #Get Page Id
        page_id = getPageID(form, request)
	if (page_id > 1):
		#Connect to app database 
		dbURL = readPgpass(app_name, user)
		engine = create_engine(dbURL)
		conn = engine.connect()
		osql = "update public.page set page_order = page_order - 1 ";
		osql += " where page_order > (select page_order from page where page_id = %s ) " % page_id ;
		conn.execute(osql)

                dsql1 = "delete from public.page_content where page_id = %s " % page_id;
                dsql2 = "delete from public.page where page_id = %s " % page_id;

                conn.execute(dsql1)
		conn.execute(dsql2)
                #Go to main index page so you can see what you have just done
                return redirect(url_for('index'))

#Define the content page : this is the standard default page for any page with content in it 
@app.route('/content', methods=['GET', 'POST'])
def content():
   #Define the WTF form used
   contentform = UpdateContent(request.form)
   jsform = UpdateJSCode(request.form)
   pageform = AddPage(request.form)

   #Get Page Id and Page Order
   page_id = getPageID(contentform, request)

   #Connect to app database so you can get the page content out of the database
   dbURL = readPgpass(app_name, user)
   engine = create_engine(dbURL)
   conn = engine.connect()

   #=======Get the Page and Table of Contents (TOC) Info as DataFrames
   pageInfo = getPageInfo(page_id, conn)
   tocInfo = getPageInfo(0, conn)

   #======Get Page Contents (Text) as DataFrame
   pageContent = getPageContent(page_id, conn)

   #====Post the Content (if it exists) and refresh the page
   didPost = postPageContent(page_id, contentform, conn)

   if (didPost):
	   return redirect(url_for(contentform.page_template.data, page_id = page_id ))

   #=======Get the Page JS Code text as a DataFrame
   pageCode = getPageCode(page_id, conn)

   #====Post the Code (if it exists) and refresh the page
   didPostJS = postJSCode(page_id, jsform, conn)

   if (didPostJS):
	   return redirect(url_for(contentform.page_template.data, page_id = page_id ))


   #Get a Dict Showing the Network of pages - note that src & tgt are purposefully reversed
   page_dict = "undefined"
   if (page_id == '1'):
      #flash(page_dict)
      #flash(type(page_dict))
      page_dict = createNetworkFromDB(conn
                        , node_tbl = 'public.page'
                        , node_id_var = 'page_id'
                        , node_name_var = 'page_name'
                        , node_grp_var = 'page_indent'
                        , node_order_var = 'page_order'
                        , link_tbl = 'public.page_relation'
                        , link_src_id_var = 'tgt_page_id' 
                        , link_tgt_id_var = 'src_page_id')

   #=============================================
   #Find out if you have a new page to write back

   if request.method == 'POST':
	   new_page_name = pageform.new_page_name.data
           new_page_title = pageform.new_page_title.data
	   new_page_content_id = pageform.new_page_content_id.data
	   new_page_code_id = pageform.new_page_code_id.data
	   max_page = pageform.max_page.data

           if (len(new_page_name.strip()) > 0):
                newsql = "insert into public.page (page_name, page_title, page_template, page_indent)";
                newsql += "Values ('%s', '%s', '%s', 1) " % (new_page_name.strip(), new_page_title.strip(), 'content') ;
		newsql += " ON CONFLICT (page_name) DO UPDATE SET page_title = '%s'" % (new_page_title.strip());  
                conn.execute(newsql)
		usql = "UPDATE public.page set page_order = (select max(page_order) + 1 from page)  where page_order is null";
                conn.execute(usql)		
		#Get the new page_id
		new_page_result = conn.execute("select max(page_id) from page")
		for r in new_page_result:
			new_page = r[0]

		#If there is a content_id, copy the content into the new page
		if (len(new_page_content_id.strip()) > 0):
			newcsql = "insert into public.content (content_md) VALUES (";
			newcsql += "(select content_md from content where content_id = %s)) " % (new_page_content_id.strip());

			conn.execute(newcsql)
			newpcsql = "insert into page_content (page_id, content_id) VALUES ( ";
			newpcsql += "(select max(page_id) from page) , ";
			newpcsql += "(select max(content_id) from content) ) ";

			conn.execute(newpcsql)
		        #If there is a content_id, copy the content into the new page
			if (len(new_page_code_id.strip()) > 0):
				newc2sql = "insert into public.jscode (jscode) VALUES (";
				newc2sql += "(select jscode from jscode where jscode_id = %s)) " % (new_page_code_id.strip());
				conn.execute(newc2sql)

				newpc2sql = "insert into page_jscode (page_id, jscode_id, jscode_show) VALUES ( ";
				newpc2sql += "(select max(page_id) from page) , ";
				newpc2sql += "(select max(jscode_id) from jscode), ";
				newpc2sql += "(select jscode_show from page_jscode where page_id = %s) " % (page_id.strip());
				newpc2sql += ") ";

				conn.execute(newpc2sql)

			return redirect(url_for('content', page_id = new_page))

                #Refresh Page so you can see what you have just done
                return redirect(url_for('content', page_id = new_page))

   #All done?  Open the web page!                                                         
   return render_template('content.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageInfo=pageInfo,
			   tocInfo=tocInfo,
                           pageContent = pageContent,
                           pageCode = pageCode,
                           dbname='',
			   pageform=pageform,
                           contentform=contentform,
			   network_dict = page_dict,
			   content_width=60,
			   code_width=20,
			   viz_width = 10
                           )

#http://adilmoujahid.com/posts/2015/01/interactive-data-visualization-d3-dc-python-mongodb/
#https://realpython.com/blog/python/web-development-with-flask-fetching-data-with-requests/

#Need to figure out what the get_data() function is (in the example, it is from the stock_scraper library
#In this example, at this point we just want to read a json file!
#Google search:  why can't i pass python dict directly to d3
#Think this has to do with fact that d3 is Javascript, so can only work with JSON

@app.route("/data")
#def data():
#    return jsonify(get_data())


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

    #Define the WTF forms used
    contentform = UpdateContent(request.form)
    pageform = AddPage(request.form)
    jsform = UpdateJSCode(request.form)

    #Get the page id
    page_id = getPageID(contentform, request)

    #Get the dbname - selected by user or default
    if request.args.get('database') is not None:
        dbname = request.args.get('database')
    elif contentform.database.data is not None:
        dbname = contentform.database.data
    else:
        dbname = 'Adventureworks'


    #=======Get Page Info as DataFrame
    pageInfo = getPageInfo(page_id, conn)
    tocInfo = getPageInfo(0, conn)

    #======Get Page Contents (Text) as DataFrame
    pageContent = getPageContent(page_id, conn)

    #====Get content that has been submitted via the form and post it
    didPost = postPageContent(page_id, contentform, conn)
    if (didPost):
        return redirect(url_for(contentform.page_template.data, page_id = page_id, database=dbname ))

    #=======Get the Page JS Code text as a DataFrame
    pageCode = getPageCode(page_id, conn)

    #====Post the Code (if it exists) and refresh the page
    didPostJS = postJSCode(page_id, jsform, conn)

    if (didPostJS):
	   return redirect(url_for(contentform.page_template.data, page_id = page_id ))

    #======================================
    #The code for showing Database info
    #======================================
    #Set the session as always logged in, for now                                                                              
    session['logged_in'] = True

    #initialize the variables
    numschema = 0; numdb = 0; note =''; schema_list = ''; allTables = '';
    allSchemas = ''; allFK = ''; num_allFK = 0; num_tables = ''; link_list = [];
    radius=50;
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
	radius=numschema*10

    #Get Network Data Structure
    output_list = getTableNetwork(dbname, user)
    
    tableDF = output_list[0]
    unique_rec = output_list[1]
    #flash(unique_rec)
    links_list = output_list[2]
    nodes_list = output_list[3]   
    network_dict = output_list[4] #a dictionary-- the same thing you get with json.loads the string
    json_dump = output_list[5]    #a string
    schema_id_list = output_list[6]

    json_dump = []

    #flash(schema_id_list)

    #flash(type(network_dict))
    #flash(network_dict)
    
    #import json
    #mjson = json.loads(json_dump)
    #flash(type(mjson))
    #flash(mjson)
    #flash(network_dict==mjson)

    #flash(len(unique_rec))
    #for i in range(0,len(unique_rec)):
	#    flash(unique_rec[i])

    i = 1
    #flash(tableDF.iloc[i]['source'])
    #flash(unique_rec.get_loc(tableDF.iloc[i]['source']))
    #flash(unique_rec.get_loc(tableDF.iloc[i]['target']))
    #flash(links_list)

    #Open the web page with the variables set (found) by the python code                                                   
    return render_template('seemedb.html', 
                           project_name = app_name, 
                           page_id = page_id ,
                           pageInfo = pageInfo,
			   tocInfo = tocInfo,
                           pageContent=pageContent,
			   pageCode=pageCode,
                           pageform=pageform,
                           dbname=dbname, 
                           username=user, numschema=numschema,
                           dbnames=dbnames, numdb=numdb, note=note,
                           schema_list = schema_list, allTables = allTables,
                           allSchemas = allSchemas, allFK = allFK, num_allFK = num_allFK,
                           num_tables=num_tables,
			   link_list = link_list,
			   tableDF = tableDF,
			   network_dict= network_dict,
			   network_str = json_dump,
			   radius=radius,
			   schema_id_list = schema_id_list,
			   content_width=60,
			   viz_width=70
			   

                           )




#==================================================
#Define the content for the JsonDB page
#  This page is the same as content, but with code added 
#=================================================
@app.route('/jsondb', methods=['GET', 'POST'])
def jsondb():
   #Define the WTF form used
   form = UpdateContent(request.form)

   #Get Page Id
   page_id = getPageID(form, request)

   #Connect to app database so you can get the page content out of the database
   dbURL = readPgpass(app_name, user)
   engine = create_engine(dbURL)
   conn = engine.connect()

   #For jsondb, query db to get the nodes/links json dict for a network


   #Determine the that page has been requested
   #If no page, go back to home
   if request.args.get('page_id') is None:
       return redirect(url_for('index'))
   #Otherwise...
   else:
        #=======Get the Page Info as a DataFrame
        pageInfo = getPageInfo(page_id, conn)

        #======Get Page Contents (Text) as DataFrame
        pageContent = getPageContent(page_id, conn)

        #====Get content that has been submitted via the form and post it
        didPost = postPageContent(page_id, form, conn)

        if (didPost):
            return redirect(url_for(form.page_template.data, page_id = page_id ))

   #All done?  Open the web page!                                                         
   return render_template('content.html', 
                           project_name = app_name, 
                           page_id=page_id,
                           pageInfo=pageInfo,
                           pageContent = pageContent,
                           dbname='',
                           form=form,
			   content_width=80,
			   code_width=0,
			   viz_width = 0
                           )





#==================================================
#Define the Register page 
#=================================================
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


