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
        # Checks if a certain property is mandatory
        for key in grouping:
            size = key[1]
            for prop in grouping[key]:
                if grouping[key][prop] == size:
                    grouping[key][prop] = True
                elif prop != 'relationships':
                    grouping[key][prop] = False

    
    def process_keys(self, grouping, new_key_name):
        # Removes the size from the key name
        processed_grouping = dict()
        for key in grouping:
            processed_grouping[(key[0], new_key_name)] = grouping[key]

        return processed_grouping


    def process_props_grouping(self, grouping, key, record, record_name):
        # Adds how many times a prop was found in the nodes or relationships with the same labels
        # Used in the post_process method to check if it is mandatory
        for prop in record[record_name].keys():
            typed = type(record[record_name].get(prop))
            prop_key = (prop, typed)
            if prop_key in grouping[key].keys():
                grouping[key][prop_key] = grouping[key][prop_key] + 1
            else:
                grouping[key][prop_key] = 1


    def process_relationships_grouping(self, grouping, key, node_id):
        # Gathers all relationships that flow out nodes with certain label
        # Checks if that realtionship is present in every node from that label or not
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


    def process_intersection(self, grouping, label, props):
        new_grouping = dict()
        for key in grouping:
            if key[0].intersection(label):
                new_key = (key[0].difference(label), 'node')
                # TODO difference relationships
                new_props = {k : grouping[key][k] for k in set(grouping[key]).difference(set(props))}
                new_grouping[new_key] = new_props
            else:
                new_grouping[key] = grouping[key]

        return new_grouping


    def intersect_props(self, grouping, intersections):
        # TODO intersect relationships
        aux_key = (next(iter(intersections)), 'node')
        new_props = grouping[aux_key]
        for label in intersections:
            new_props = {k : grouping[aux_key][k] for k in set(new_props).intersection(set(grouping[(label, 'node')]))}

        print(new_props)
        return new_props


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
        unique_labels_processed = dict()
        iteration = 0

        labels_to_process = True
        while labels_to_process:
            print('\n -------- ITERATION ' + str(iteration) + ' -------- \n')
            iteration += 1
            labels_to_process = False
                
            labels_combinations = {k[0] for k in grouping_nodes.keys()}
            print(labels_combinations)
       
            labels_len_1 = set()
            for label in labels_combinations:
                if len(label) == 1:
                    unique_labels_processed[label] = grouping_nodes.pop((label, 'node'))
                    labels_to_process = True
                    labels_len_1.add(label)

            if labels_to_process:
                for l in labels_len_1:
                    grouping_nodes = self.process_intersection(grouping_nodes, l, unique_labels_processed[l])

            else:
                intersections = dict()
                for l1 in labels_combinations:
                    for l2 in labels_combinations:
                        l3 = l1.intersection(l2)
                        if len(l3) == 1:
                            if l3 not in intersections.keys():
                                intersections[l3] = {l1, l2}
                            else:
                                intersections[l3].add(l1)
                                intersections[l3].add(l2)

                if len(intersections) > 0:
                    labels_to_process = True
                    key_with_most_intersections = next(iter(intersections))
                    for k in intersections:
                        if len(intersections[k]) > len(intersections[key_with_most_intersections]):
                            key_with_most_intersections = k

                    print(key_with_most_intersections)
                    print(intersections[key_with_most_intersections])
                    unique_labels_processed[key_with_most_intersections] = self.intersect_props(grouping_nodes, intersections[key_with_most_intersections])
                    grouping_nodes = self.process_intersection(grouping_nodes, key_with_most_intersections, unique_labels_processed[key_with_most_intersections])
    
        return unique_labels_processed


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

    for k in grouping:
        print(k, grouping[k])
