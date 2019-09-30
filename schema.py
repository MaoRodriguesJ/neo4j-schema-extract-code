from driver import Driver
from query import Query
from itertools import chain, combinations
import sys

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

                # TODO I will try the intersection OR difference of relationships later
                #self.process_relationships_grouping(grouping, key, record['node'].id)

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

        # TODO As the relationships have unique type/label nothing more is needed after this
        grouping_relationships = dict() #self.grouping_relationships()
 
        return {**grouping_nodes, **grouping_relationships}


    def test_intersection(self, grouping, label, props):
        # TODO intersect or difference props and relationships (part 3 of the explanation below)
        return None


    def test(self):
        # TODO The seconod part of the algorithm divided in 2 parts
        # 1. find unique labels, use them to remove their properties of the ones 
        #    that have multiple labels with this unique one in them
        # 2. when all the uniques are done, this means the ones that turned uniques too
        #    there is only the multiple ones left, so we decide wether we are intersecting
        #    or differencing them, we search for length 1 intersection or difference, after done
        #    it will create a new unique label and we iterate over 1 again
        # 3. inside those two parts we need to intersect or difference the properties and relationships sets
        #    and need to fix the grouping nodes with it

        grouping_nodes = self.grouping_nodes()
        intersections = dict()

        label_with_len_1 = True
        while label_with_len_1:
            labels_combinations = {k[0] for k in grouping_nodes.keys()}
            print('Labels combinations: ' + str(labels_combinations))
       
            label_with_len_1 = False
            labels_len_1 = set()
            for label in labels_combinations:
                if len(label) == 1:
                    print('Label with length 1: ' + str(label))
                    intersections[label] = grouping_nodes.pop((label, 'node'))
                    label_with_len_1 = True
                    labels_len_1.add(label)

            if label_with_len_1:
                for l in labels_len_1:
                    self.test_intersection(grouping_nodes, l, intersections[l])

            else:
                for l1 in labels_combinations:
                    for l2 in labels_combinations:
                        l3 = l1.intersection(l2)
                        # TODO order matters in difference
                        l4 = l1.difference(l2)
                        if len(l3) == 1:
                            print('Intersection: ' + str(l1) + ' |intersect| ' + str(l2) + ' = ' + str(l3))

                        if len(l4) == 1:
                             print('Difference: ' + str(l1) + ' |diff| ' + str(l2) + ' = ' + str(l4))
                
        for i in intersections:
            print('Intersections length 1: ' + str(i))

        return intersections


if __name__ == '__main__':
    url = "bolt://0.0.0.0:7687"
    login = "neo4j"
    password = "neo4jadmin"
    if len(sys.argv) == 4:
        url = sys.argv[1]
        login = sys.argv[2]
        password = sys.argv[3]

    driver = Driver(url, login, password)
    schema = SchemaExtractor(driver)
    grouping = schema.test()

    # for k in grouping:
    #     print(k, grouping[k])
