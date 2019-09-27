from driver import Driver
from query import Query
from itertools import chain, combinations

class SchemaExtractor():

    def __init__(self, driver):
        self._driver = driver


    def powerset(self, iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        tuples = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
        return filter(None, map(frozenset, tuples))


    def get_labels(self):
        return [l['label'] for l in self._driver.read_transaction(Query._get_labels)]


    def get_labels_combination(self, labels):
        return self.powerset(labels)


    def get_nodes_by_labels(self, labels):
        params = {}
        for index, value in enumerate(labels):
            params['label' + str(index)] = value
        
        return self._driver.read_transaction(Query._get_nodes_by_label, params)

    
    def get_relations_types_by_id(self, node_id):
        params = {'id' : node_id}
        return self._driver.read_transaction(Query._get_relations_types_by_id, params)


    def get_relationship_types(self):
        return [t['relationshipType'] for t in self._driver.read_transaction(Query._get_types)]


    def process_properties_grouping(self, grouping, key, record):
        for prop in record['node'].keys():
            typed = type(record['node'].get(prop))
            prop_key = (prop, typed)
            if prop_key in grouping[key].keys():
                grouping[key][prop_key] = grouping[key][prop_key] + 1
            else:
                grouping[key][prop_key] = 1


    def process_relations_grouping(self, grouping, key, node_id):
        relationships = self.get_relations_types_by_id(node_id)
        if 'relationships' not in grouping[key].keys():
            grouping[key]['relationships'] = dict()
            for r in relationships:
                relation_key = (r['relation'], frozenset(r['labels']))
                grouping[key]['relationships'][relation_key] = True
        
        else:
            relationships_keys = set()
            old_keys = grouping[key]['relationships'].keys()
            for r in relationships:
                relation_key = (r['relation'], frozenset(r['labels']))
                relationships_keys.add(relation_key)
                if relation_key not in old_keys:
                    grouping[key]['relationships'][relation_key] = False

            for k in old_keys:
                if k not in relationships_keys:
                    grouping[key]['relationships'][k] = False


    def process_relations_props(self, grouping):
        return None


    def grouping(self):
        labels_powerset = self.get_labels_combination(self.get_labels())
        grouping = dict()
        for label_combination in labels_powerset:
            records = [r for r in self.get_nodes_by_labels(label_combination)]
            key = (label_combination, len(records))
            grouping[key] = dict()
            for record in records:
                self.process_properties_grouping(grouping, key, record)
                self.process_relations_grouping(grouping, key, record['node'].id)

        self.process_relations_props(grouping)
        
        return grouping


if __name__ == '__main__':
    driver = Driver("bolt://0.0.0.0:7687", "neo4j", "neo4jadmin")
    schema = SchemaExtractor(driver)
    grouping = schema.grouping()

    for k in grouping:
        print(k, grouping[k])
