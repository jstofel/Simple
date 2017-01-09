
#================================
##Debugging: show error and exit
#================================
def fatal(*L):
     print >>sys.stderr, ''.join(L)
     raise SystemExit

#=======================================
##  Read database password out of .pgpass
##  Specfic password file for PostgreSQL,
##    on Unix and Mac
##  Returns a connection string
#=======================================
def readPgpass(dbName, user):
    #Read the pgpass file 
    protocol = 'postgresql'
    URL_FORMAT = "%s://%s:%s@%s/%s"
    fname = "/Users/"+user+"/.pgpass"
    f = open(fname, 'rb')
    for a in f.readlines():
      host, port, database, username, password = a.rstrip().split(':')
      if (database == dbName):
          engineURL = URL_FORMAT % (protocol, username, password, host, database)
      elif (database == '*'):
          engineURL = URL_FORMAT % (protocol, username, password, host, dbName)
    return(engineURL)

#=================================================================================
##Get Database Names out of Postgresql
## Makes the connection using the name of the default database, which for PostgreSQL
##   is 'postgres'.  We do this because the connection has to be to a named database,
##   but once we have made the connection we have access to all database names through
##   the information schema.  Note that this particular set of requirements is specific
##   to PostgreSQL. For other engines (Sql Server, Teradata, Oracle) we would need
##   different functions to get the same result (or add engine type to this function)
## Requires: readPgpass, fatal
## Returns:  list of database names
#==================================================================================
def getPgDBnames(user):
    #get sqlalchemy functions to use
    from sqlalchemy import create_engine, engine, exc
    #make the connection usng the default database for the type
    svURL = readPgpass('postgres', user)
    #the query that gets the database names: this query is not misspelled!
    dbq = 'select datname from pg_database where datacl is null order by datname'
    try:
        engine = create_engine(svURL)
        conn = engine.connect()
        dbnames = conn.execute(dbq)
        conn.close()
        return(dbnames)
    except exc.SQLAlchemyError as detail:
        print(dbq)
        fatal("Could not query : %s" % detail)

#=================================================================================
##Get Schema Names out of a named database
##
## Requires:  readPgpass, fatal
## Returns: list of schema names
#=================================================================================
def getSchemas(database, user):
    #get sqlalchemy functions to use
    from sqlalchemy import create_engine, engine, exc, engine
    from sqlalchemy.engine import reflection
    #make the connection using the specified database
    dbURL = readPgpass(database, user)
    try:
        db = create_engine(dbURL)
        insp = reflection.Inspector.from_engine(db)
        schema_list = insp.get_schema_names()
        return(schema_list)
    except exc.SQLAlchemyError as detail:
        fatal("Could not query : %s" % detail)



#==========================================================================
##Create Application Database if it does not already exist                 
##NOT DONE
#==========================================================================                                    
def makeDB(dbName, user):
     if dbName in dbnames:
          protocol = 'postgresql'
          URL_FORMAT = "%s://%s:%s@%s/%s"
          fname = "/Users/"+user+"/.pgpass"
          f = open(fname, 'rb')
          for a in f.readlines():
               host, port, database, username, password = a.rstrip().split(':')
               if (database == dbName):
                    engineURL = URL_FORMAT % (protocol, username, password, host, database)
               elif (database == '*'):
                    engineURL = URL_FORMAT % (protocol, username, password, host, dbName)
               else:
                    engineURL = ''
          try:
               engine = create_engine(engineURL)
               meta = engine.connect()
          except exc.SQLAlchemyError as detail:
               print(engineURL)
               fatal("Could not query : %s" % detail)
     else:
          dbName = 'Database ' + dbName + ' Not Found'



#=================================================================================
##Get Tables by Schema out of named Database
##
## Requires:  readPgpass, fatal
## Returns: pandas dataframe of tables by schema, listing foreign key constraints 
#=================================================================================
def getTables(database, user):
    #get sqlalchemy functions to use
    from sqlalchemy import create_engine, engine, exc, engine
    from sqlalchemy.engine import reflection
    import pandas as pd
    #Note - Schema names and table names come out as lists
    # To put them together I make pandas dataframes 
    # The output of other methods, like get_sorted_table_and_fkc_names is a list of dictionaries
    # Methods around foreign keys:
    #  get_sorted_table_and_fkc_names (tablename, [(tname,fkname),(tname, fkname),...]) ends w (None, [(tname,fkname),(tname, fkname),...])
    #  get_foreign_keys(table_name, schema=) returns list of dicts with these keys:
    #    constrained_columns, referred_schema, referred_table, referred_columns, name(optional name of constraint)
    allTables = pd.DataFrame({'schema' : [] , 'table' : [] })
    allSchemas = pd.DataFrame({'schema' : [] , 'numtable' : [] })
    allFK = []  #This will be a list of all lists of dicts for the foreign keys
    #make the connection using the specified database
    dbURL = readPgpass(database, user)
    try:
        db = create_engine(dbURL)
        insp = reflection.Inspector.from_engine(db)
        s_list = insp.get_schema_names() #List of names
        for s in s_list:
            tables = insp.get_table_names(schema=s)  #List of table names
            for t in tables:
                #Get list of dicts describing foreign key relations
                fkt = insp.get_foreign_keys(t, schema = s)
                #Add schema name and table name to each dict in list
                for i in fkt:
                    i['schema'] = s 
                    i['table'] = t
                #Add the dictionary to the list of all dictionaries
                allFK = allFK + fkt
            #Make a dataframe for all table names in this schema (if none, empty frame is made)
            tf = pd.DataFrame({'schema' : s, 'table' : tables})
            #Make a dataframe for count of tables in schema, only if there are tables in schema
            sf = pd.DataFrame({'schema' : [] , 'numtable' : [] })
            if len(tables) > 0 :
                sf = pd.DataFrame({'schema' : s, 'numtable' : [len(tables)] })

            # How to get information out of the pandas data frame
            #for index, row in tf.iterrows():
            #    print row['schema'], row['table']
            #Add the by-table data frames to the overall data frames
            allTables = pd.concat([allTables, tf], ignore_index=True)
            allSchemas = pd.concat([allSchemas, sf], ignore_index=True)
            #Make a list of objects to return
            returnList = [allTables, allSchemas, allFK]
        return returnList

    except exc.SQLAlchemyError as detail:
        fatal("Could not query : %s" % detail)


        
    
