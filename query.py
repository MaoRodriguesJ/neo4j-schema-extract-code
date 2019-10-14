class Query():
    # All queries used in the extraction process

    @staticmethod
    def _get_types(tx):
        # Get all relationship types
        return tx.run("call db.relationshipTypes")


    @staticmethod
    def _get_labels(tx):
        # Get all nodes labels
        return tx.run("call db.labels")


    @staticmethod
    def _get_nodes_by_label(tx, params):
        # Get a list of nodes that have exactly the labels passed by parameter
        query = "match (node) where "
        for key in params:
            query = query + "$" + key + " in labels(node) and "
            
        query = query + "length(labels(node))=" + str(len(params)) + " return node"
        return tx.run(query, params)


    @staticmethod
    def _get_relationships_types_by_id(tx, params):
        # From a node get a list of relationships types that flow out of it and the labels of the nodes its reaching
        return tx.run("match (node)-[relationship]->(end_node) where id(node)=$id "+
                      "return type(relationship) as relationship, labels(end_node) as labels", params)


    @staticmethod
    def _get_relationships_by_type(tx, params):
        # Get a list of relationships by its type
        return tx.run("match ()-[relationship]-() where type(relationship)=$type return relationship", params)
    