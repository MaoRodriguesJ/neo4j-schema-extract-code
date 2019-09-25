from driver import Driver
from query import Query
from itertools import chain, combinations

class SchemaExtractor():

    def __init__(self, driver):
        self._driver = driver

    def powerset(self, iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))

    def get_relationship_types(self):
        return [t['relationshipType'] for t in self._driver.read_transaction(Query._get_types)]

    def get_labels(self):
        return [l['label'] for l in self._driver.read_transaction(Query._get_labels)]

    def get_labels_combination(self, labels):
        return self.powerset(labels)

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

    def get_nodes_passing_labels(self, labels):
        params = {}
        for index, value in enumerate(labels):
            params['label' + str(i)] = j
        nodes = self._driver.read_transaction(Query._get_nodes_passing_label, params)
        for n in nodes:
            print(n)

if __name__ == '__main__':
    driver = Driver("bolt://0.0.0.0:7687", "neo4j", "neo4jadmin")
    schema = SchemaExtractor(driver)
    schema.get_nodes_passing_labels(['User', 'Movie'])
