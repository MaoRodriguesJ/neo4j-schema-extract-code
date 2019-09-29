class Query():

    @staticmethod
    def _get_types(tx):
        return tx.run("call db.relationshipTypes")


    @staticmethod
    def _get_labels(tx):
        return tx.run("call db.labels")


    @staticmethod
    def _get_schema(tx):
        return tx.run("call db.schema")


    @staticmethod
    def _get_nodes_by_label(tx, params):
        query = "match (node) where "
        for key in params:
            query = query + "$" + key + " in labels(node) and "
            
        query = query + "length(labels(node))=" + str(len(params)) + " return node"
        return tx.run(query, params)


    @staticmethod
    def _get_relationships_types_by_id(tx, params):
        return tx.run("match (node)-[relationship]->(end_node) where id(node)=$id "+
                      "return type(relationship) as relationship, labels(end_node) as labels", params)


    @staticmethod
    def _get_relationships_by_type(tx, params):
        return tx.run("match ()-[relationship]-() where type(relationship)=$type return relationship", params)
    