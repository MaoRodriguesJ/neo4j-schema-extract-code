from driver import Driver
from query import Query

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
