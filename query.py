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
    def _get_nodes_passing_label(tx, params):
        query = "match (a) where "
        for key, _ in params:
            query = query + "$" + key + " in labels(a) and "
            
        params['size'] = len(params)
        return tx.run("match (a) where $label in labels(a) and length(labels(a))=1 return a", params)