
#===========================================================================                  
#  Application Functions                                                                         
#===========================================================================                  
from flask import flash;  #for debugging messages

def getPageID(form, request):
    if request.args.get('page_id') is not None:
        page_id = request.args.get('page_id')
    elif form.page_id.data is not None:
        page_id = form.page_id.data
    else:
        page_id = 0
    return str(page_id)

def pageNav(a):
    #Determine what page has been requested
    from flask import url_for
    if a.get('page_title') is None:
        page_title=''; page_name='index';
        url = url_for('index');
    else:
        page_title = a.get('page_title');
        if a.get('page_name') is None:
            page_name = page_title;
        else:
            page_name = a.get('page_name')
        url = url_for('index')+"?page_title="+page_title+"&page_name="+page_name;
    return(page_name, page_title, url)

def getPageInfo(page_id, conn):
    if int(page_id) > 0:

        psql = "select s.page_id , s.page_name, s.page_title, s.page_template, s.page_level, " ;
        psql += " case when length(s.content_md) > 1 then 1 else 0 end as has_content, ";
        psql += "p1.page_id as next_page_id , p1.page_template as next_page_template, ";
        psql += "case when p2.page_template != 'index' then p2.page_id end as prev_page_id, " ;
        psql += "case when p2.page_template != 'index' then p2.page_template else '\' end  as prev_page_template from " ;
        psql += "(select p.*, c.content_md, p.page_order + 1 as next_page_order, p.page_order - 1 as prev_page_order " ;
        psql += "from page p left join page_content pc on p.page_id = pc.page_id left join content c on pc.content_id = c.content_id  "
        psql += "where p.page_id = %s ) s " % (page_id) ;
        psql += "left join page p1  on p1.page_order = s.next_page_order "; 
        psql += "left join page p2 on p2.page_order = s.prev_page_order ";


    else:
        psql = "select page_id, page_name, page_title, page_template, page_level, 0 as has_content , " ;
        psql += "0 as next_page_id, 'content' as next_page_template, ";
        psql += "0 as prev_page_id, 'content' as prev_page_template ";
        psql += "from public.page order by page_order";

    result = conn.execute(psql);
    fetchall = result.fetchall()
    import pandas as pd
    pageInfo = pd.DataFrame(fetchall, columns=['page_id', 'page_name', 'page_title', 'page_template', 'page_level', 'has_content', 'next_page_id', 'next_page_template',  'prev_page_id', 'prev_page_template'])
    return pageInfo

def getPageContent(page_id, conn):
    if (page_id is None) or (int(page_id) == 0) :
        fatal("getPageContent function requires a numeric page_id argument > 0")
    csql = "select c.content_id, c.content_md from public.content c ";
    csql += "join public.page_content pc on c.content_id = pc.content_id ";
    csql += "join public.page p on p.page_id = pc.page_id ";
    csql += "where pc.page_id = %s " % page_id; 
    result = conn.execute(csql);
    fetchall = result.fetchall();

    import pandas as pd
    pageContent = pd.DataFrame(fetchall, columns=['content_id','content_md'] )
    return pageContent


def getPageCode(page_id, conn):
    if (page_id is None) or (int(page_id) == 0) :
        fatal("getPageCode function requires a numeric page_id argument > 0")
    csql = "select p.page_id, ";
    csql += "case when c.jscode_id is null then 0 else c.jscode_id end as jscode_id, " ;
    csql += "case when c.jscode is null then '' else c.jscode end as jscode, "
    csql += "case when pc.jscode_show = 1 then 'block' else 'none' end as jscode_display, "
    csql += "case when pc.jscode_show = 1 then 'none' else 'block' end as jscode_edit, "
    csql += "case when pc.jscode_show = 1 then 30 else 70 end as content_width "
    csql += "from public.page p ";
    csql += "left join public.page_jscode pc on p.page_id = pc.page_id ";
    csql += "left join public.jscode c on c.jscode_id = pc.jscode_id ";
    csql += "where p.page_id = %s " % page_id; 
    result = conn.execute(csql);
    fetchall = result.fetchall();

    #flash(csql);

    import pandas as pd
    pageCode = pd.DataFrame(fetchall, columns=['page_id', 'jscode_id','jscode', 'jscode_display', 'jscode_edit', 'content_width'] )
    return pageCode



def postPageContent(page_id, form, conn):
    #Get content that has been submitted via the form                                         
    new_content_md = form.content_md.data
    content_id = form.content_id.data
    target = form.page_template.data

    if new_content_md is not None:
        if (len(new_content_md.strip()) > 0):
            if content_id > '0':
                #Excape ' and % by doubling them
                esc_content = new_content_md.replace("'", "''").replace("%","%%")
                #If there are script tags, you need to insert a space before the word 'script'
                # And also add a usage note. Define usage note here.
                sn1 = "###Note: if you copy a script off this page to paste and use in your own code, "
                sn2 = "make sure to remove the space between the ```<``` and  ```</``` openers "
                sn3 = "and their associated ```script``` keyword, in order to make the script executable."
                sn = sn1 + sn2 + sn3
                # First, check if there is <script or </script
                fs = "<script"
                fso = esc_content.find(fs)
                if (fso >= 0):
                    esc_content = esc_content.replace("<script", "< script").replace("</script", "</ script")
                    fno = esc_content.find(sn)
                    if (fno <= 0):
                        fto = esc_content.find("```", fso) + 3
                        #Note - you want to slice the string into 2 parts: from 0 to fto, and from fto to end
                        a = esc_content[:fto]
                        b = esc_content[fto:]
                        esc_content = a + sn + "   " + b
                    #    #Find the first ``` after fso
                    #    #Split the string
                    #    #Put the note in the string

                contsql = "update public.content set "
                contsql += "content_md = '%s' where content_id = %s " % (esc_content, str(content_id));
                xsql = ''
                #flash(contsql)
                conn.execute(contsql)
            else:
                contsql = "insert into public.content (content_md) VALUES ";
                contsql += "('%s')" % (new_content_md);
                xsql = "insert into public.page_content "
                xsql += "(select %s as page_id, max(content_id) as content_id from public.content) " % str(page_id);

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

def postJSCode(page_id, form, conn):
    #Get content that has been submitted via the form                                         
    new_jscode = form.jscode.data
    jscode_id = form.jscode_id.data
    target = form.page_template.data

    if new_jscode is not None:
        if (len(new_jscode.strip()) > 0):
            #Excape ' and % by doubling them
            esc_jscode = new_jscode.strip().replace("'", "''").replace("%","%%")
            #flash("Escaped code "+esc_jscode)
            if jscode_id > '0':
                contsql = "update public.jscode set "
                contsql += "jscode = '%s' where jscode_id = %s " % (esc_jscode, str(jscode_id));
                xsql = ''
                #flash(contsql)
                conn.execute(contsql)
            else:
                contsql = "insert into public.jscode (jscode) VALUES ";
                contsql += "('%s')" % (esc_jscode);
                xsql = "insert into public.page_jscode "
                xsql += "(select %s as page_id, max(jscode_id) as jscode_id from public.jscode) " % str(page_id);

                #Note: not the most ironclad process to insert on content table, then insert on linking table
                #  using the new jscode_id that was just created by the insert, but it works in dev
                #flash(contsql)
                #flash(xsql)
                conn.execute(contsql)
                conn.execute(xsql)

            #Return True: the update was run                                                  
            return True
        else:
            return False
    else:
        return False
