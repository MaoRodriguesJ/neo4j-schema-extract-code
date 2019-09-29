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

    
    def get_relationships_types_by_id(self, node_id):
        params = {'id' : node_id}
        return self._driver.read_transaction(Query._get_relationships_types_by_id, params)


    def get_relationship_types(self):
        return [t['relationshipType'] for t in self._driver.read_transaction(Query._get_types)]

    
    def get_relationships_by_type(self, typed):
        params = {'type': typed}
        return self._driver.read_transaction(Query._get_relationships_by_type, params)


    def post_process(self, grouping):
        for key in grouping:
            size = key[1]
            for prop in grouping[key]:
                if grouping[key][prop] == size:
                    grouping[key][prop] = True
                elif prop != 'relationships':
                    grouping[key][prop] = False

    
    def process_keys(self, grouping, new_key_name):
        processed_grouping = dict()
        for key in grouping:
            processed_grouping[(key[0], new_key_name)] = grouping[key]

        return processed_grouping


    def process_props_grouping(self, grouping, key, record, record_name):
        for prop in record[record_name].keys():
            typed = type(record[record_name].get(prop))
            prop_key = (prop, typed)
            if prop_key in grouping[key].keys():
                grouping[key][prop_key] = grouping[key][prop_key] + 1
            else:
                grouping[key][prop_key] = 1


    def process_relationships_grouping(self, grouping, key, node_id):
        relationships = self.get_relationships_types_by_id(node_id)
        if 'relationships' not in grouping[key].keys():
            grouping[key]['relationships'] = dict()
            for r in relationships:
                relationship_key = (r['relationship'], r['labels'][0])
                grouping[key]['relationships'][relationship_key] = True
        
        else:
            relationships_keys = set()
            old_keys = grouping[key]['relationships'].keys()
            for r in relationships:
                relationship_key = (r['relationship'], r['labels'][0])
                relationships_keys.add(relationship_key)
                if relationship_key not in old_keys:
                    grouping[key]['relationships'][relationship_key] = False

            for k in old_keys:
                if k not in relationships_keys:
                    grouping[key]['relationships'][k] = False


    def grouping_nodes(self):
        labels_powerset = self.get_labels_combination(self.get_labels())
        grouping = dict()
        for label_combination in labels_powerset:
            records = [r for r in self.get_nodes_by_labels(label_combination)]
            if len(records) == 0:
                continue

            key = (label_combination, len(records))
            grouping[key] = dict()
            for record in records:
                self.process_props_grouping(grouping, key, record, 'node')
                self.process_relationships_grouping(grouping, key, record['node'].id)

        self.post_process(grouping)
        return self.process_keys(grouping, 'node')


    def grouping_relationships(self):
        types = self.get_relationship_types()
        grouping = dict()
        for typed in types:
            records = [r for r in self.get_relationships_by_type(typed)]
            if len(records) == 0:
                continue

            key = (typed, len(records))
            grouping[key] = dict()
            for record in records:
                self.process_props_grouping(grouping, key, record, 'relationship')

        self.post_process(grouping)
        return self.process_keys(grouping, 'relationship')


    def grouping(self):
        grouping_nodes = self.grouping_nodes()
        grouping_relationships = self.grouping_relationships()
 
        return {**grouping_nodes, **grouping_relationships}


if __name__ == '__main__':
    driver = Driver("bolt://0.0.0.0:7687", "neo4j", "neo4jadmin")
    schema = SchemaExtractor(driver)
    grouping = schema.grouping()

    for k in grouping:
        print(k, grouping[k])
