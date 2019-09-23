from neo4j.v1 import GraphDatabase

class ReturnTests():

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def get_relationship_types(self):
        with self._driver.session() as session:
            types = session.write_transaction(self._get_types)
            for t in types:
                print(t['relationshipType'])

    def get_labels(self):
       with self._driver.session() as session:
            labels = session.write_transaction(self._get_labels)
            for l in labels:
                print(l['label'])

    def get_schema(self):
        with self._driver.session() as session:
            schema = session.write_transaction(self._get_schema)
            for s in schema:
                for n in s['nodes']:
                    print(n.labels)
                    print(n.items())    # this is not a dict, its an iterable
                                        # but there is the constraints values for nodes here
                print('\n')
                for r in s['relationships']:
                    print(r.type)
                    print(r.nodes)
                    print(r.items())
    
    def get_property_keys(self):
        with self._driver.session() as session:
            properties = session.write_transaction(self._get_properties_keys)
            for p in properties:
                print(p['propertyKey'])

    def get_nodes_passing_label(self, label):
        with self._driver.session() as session:
            nodes = session.read_transaction(self._get_nodes_passing_label, {'label': label})
            for n in nodes:
                print(n)

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


driver = ReturnTests("bolt://0.0.0.0:7687", "neo4j", "neo4jadmin")
driver.get_nodes_passing_label('User')
