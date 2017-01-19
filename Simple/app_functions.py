
#===========================================================================                  
#  Application Functions                                                                         
#===========================================================================                  

def getPageID(form, request):
    if request.args.get('page_id') is not None:
        page_id = request.args.get('page_id')
    elif form.page_id.data is not None:
        page_id = form.page_id.data
    else:
        page_id = 0
    return str(page_id)

def getPageInfo(page_id, conn):
    if int(page_id) > 0:
        psql = "select * from public.page where page_id = %s " % (page_id);
    else:
        psql = "select * from public.page order by page_id";
    result = conn.execute(psql);
    fetchall = result.fetchall()
    import pandas as pd
    pageInfo = pd.DataFrame(fetchall, columns=['page_id', 'page_name', 'page_title', 'page_target'])
    return pageInfo

def getPageContent(page_id, conn):
    if (page_id is None) or (int(page_id) == 0) :
        fatal("getPageContent function requires a numeric page_id argument > 0")
    csql = "select c.content_id, c.content_md, c.content_ht from public.content c ";
    csql += "join public.page_content pc on c.content_id = pc.content_id ";
    csql += "join public.page p on p.page_id = pc.page_id ";
    csql += "where pc.page_id = %s " % page_id; 
    result = conn.execute(csql);
    fetchall = result.fetchall()
    import pandas as pd
    pageContent = pd.DataFrame(fetchall, columns=['content_id','content_md', 'content_ht'] )
    return pageContent

def postPageContent(page_id, form, conn):
    #Get content that has been submitted via the form                                         
    new_content_md = form.content_md.data
    new_content_ht = form.content_ht.data
    content_id = form.content_id.data
    target = form.page_target.data
    #flash("The target is '"+str(target)+"'")                                                 

    if new_content_md is not None:
        if (len(new_content_md.strip()) > 0):
            if content_id > '0':
                contsql = "update public.content set "
                contsql += "content_md = '%s', content_ht = '%s' where content_id = %s " % (new_content_md, new_content_ht, str(content_id));
                xsql = ''
                conn.execute(contsql)
            else:
                contsql = "insert into public.content (content_md, content_ht) VALUES ";
                contsql += "('%s', '%s')" % (new_content_md, new_content_ht);
                xsql = "insert into public.page_content "
                xsql += "(select %s as page_id, max(content_id) as content_id from public.con\
tent) " % str(page_id);

                #Note: not the most ironclad process to insert on content table, then insert on linking table
                #  using the new content_id that was just created by the insert, but it works in dev
                conn.execute(contsql)
                conn.execute(xsql)

            #Return True: the update was run                                                  
            return True
        else:
            return False
    else:
        return False
