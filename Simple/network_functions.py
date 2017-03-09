#======================================================================
##Create Network Diagram JSON from a Table with Source-ID and Target-ID
#======================================================================
def createNetworkFromDB(database, user, tbl, srcvar, tgtvar):
    #Initialize lists
    nodes_list = []
    links_list = []
    #Make the connection using the specified database
    dbURL = readPgpass(database, user)
    try:
        engine = create_engine(dbURL)
        conn = engine.connect()
        nq = "select " + tgtvar + "from " + tbl ;
        nodes_list = conn.execute(nq)
        return [nodes_list]
    except exc.SQLAlchemyError as detail:
        fatal("Could not query : %s" % detail)
