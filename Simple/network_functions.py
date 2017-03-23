#======================================================================
##Create Network Diagram JSON from a Table with Source-ID and Target-ID
#======================================================================
def createNetworkFromDB(conn
                        , node_tbl
                        , node_id_var
                        , node_name_var
                        , node_grp_var
                        , node_order_var
                        , link_tbl
                        , link_src_id_var
                        , link_tgt_id_var):
        #This function allows the user to create a network diagram out 
        # of one (or two) tables in a database
        #====Get Nodes and Convert to List of Dicts ==#                                                      
        tnq =  "select " + node_name_var + " as name, " + node_grp_var + " as group ";
        tnq += "from " + node_tbl + " order by " + node_order_var + "; "

        node_proxy = conn.execute(tnq)
        node_list = [dict(r) for r in node_proxy]

        #===Get List of Relationships as Link List ==#                                                 
        #   Assign index number to ordered nodes                                                       
        iq = "select row_number() over (order by " + node_order_var + " nulls last) - 1 as idx"
        iq += ", " + node_id_var + ", " + node_name_var + " from " + node_tbl

        #   Assign the source and targets by index number                                              
        lq = "select s.idx as source, t.idx as target, 1 as weight from "
        lq += link_tbl + " r"
        lq += " join ("+iq+") as s on s."+node_id_var+" = r."+link_src_id_var ;
        lq += " join ("+iq+") as t on t."+node_id_var+" = r."+link_tgt_id_var ;

        #====Get Links and Convert to List of Dicts ==#                                                      
        link_proxy = conn.execute(lq)
        link_list = [dict(r) for r in link_proxy]

        #====Make the Final Network Dict
        from collections import defaultdict
	import json

        d = defaultdict(list)
        for n in node_list:
                d["nodes"].append(n)
        for l in link_list:
                d["links"].append(l)

        network_dict = json.dumps(d)

        return network_dict

