from Simple import app

from flask import Flask, redirect, url_for, request, session, g,  abort, render_template, flash


##Define Project Level Variables
project_name='Simple';

##Define the Views (HTML pages)                                                

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
        url = url_for(page_title);
    #Open the web page                                                         
    return render_template('index.html', 
                           project_name = project_name, page_name=page_name, 
                           page_title=page_title,
                           url = url
                           )

