from neo4j.v1 import GraphDatabase

class Driver():

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def read_transaction(self, query, parameters):
        with self._driver.session() as session:
            return session.read_transaction(query, parameters)

    def write_transaction(self, query, parameters):
        with self._driver.session() as session:
            return session.write_transaction(query, parameters)

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

class SchemaExtractor():

    def __init__(self, driver):
        self._driver = driver

    def get_relationship_types(self):
        types = self._driver.read_transaction(Query._get_types)
        for t in types:
            print(t['relationshipType'])

    def get_labels(self):
        labels = self._driver.read_transaction(Query._get_labels)
        for l in labels:
            print(l['label'])

    def get_schema(self):
        schema = self._driver.read_transaction(Query._get_schema)
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
        properties = self._driver.read_transaction(Query._get_properties_keys)
        for p in properties:
            print(p['propertyKey'])

    def get_nodes_passing_label(self, label):
        nodes = self._driver.read_transaction(Query._get_nodes_passing_label, {'label': label})
        for n in nodes:
            print(n)

if __name__ == '__main__':
    driver = Driver("bolt://0.0.0.0:7687", "neo4j", "neo4jadmin")
    schema = SchemaExtractor(driver)
    schema.get_nodes_passing_label('User')
