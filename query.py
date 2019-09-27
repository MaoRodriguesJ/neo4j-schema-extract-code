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
    def _get_relations_types_by_id(tx, params):
        return tx.run("match (node)-[relation]->(end_node) where id(node)=$id "+
                      "return type(relation) as relation, labels(end_node) as labels", params)