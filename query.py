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
    def _get_properties_keys(tx):
        return tx.run("call db.propertyKeys")

    @staticmethod
    def _get_nodes_passing_label(tx, dict):
        return tx.run("match (a) where $label in labels(a) and length(labels(a))=1 return a", dict)