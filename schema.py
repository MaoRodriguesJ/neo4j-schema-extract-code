from collator import Collator
from database import Database
from driver import Driver
import sys

class SchemaExtractor():
    # The second part of the algorithm, The SchemaExtractor
    # 1. To process the multilabel nodes we could have two approaches using sets theory:
    #       
    #           1: Use intersection, when the intersection of two multilabel nodes results
    #              in only one label we could then extract the properties and relationships
    #              that belong to that particular label
    #
    #           2: Use difference, and the same as the intersection with the difference
    #              between two multilabel nodes results in only one label
    #   
    #   But the intersection can be done with more than just two multilabel nodes because 
    #   its order does not matter and thats not true with difference
    #
    # 2. With intersection its simple, find multilabel nodes that intersect forming only one
    #    label, intersect the properties and the relationships of those multilabel too to form
    #    a new entry in the dictionary that has only one label (intersect_props_relationships method), 
    #    than extract this label and its relationships and properties from those multilabel 
    #    (process_intersection method) and reapeat this process until only one label nodes rest or we dont 
    #    have any other options to infer how those left multilabel ones could be split

    def __init__(self, driver):
        self._collator = Collator(Database(driver))


    @staticmethod
    def print_grouping_nodes(grouping):
        for k in grouping:
            print('\nKey: ' + str(k))
            print('Properties: ' +str(grouping[k]['props']))
            if len(k) == 1:
                print('Relationships: ' + str(grouping[k]['relationships']))


    def process_intersection(self, grouping, label, props):
        new_grouping = dict()
        for key in grouping:
            if key[0].intersection(label):
                new_key = (key[0].difference(label), 'node')
                new_props = {k : grouping[key]['props'][k] for k in set(grouping[key]['props']).difference(set(props['props']))}
                new_relationships = {k : grouping[key]['relationships'][k] for k in set(grouping[key]['relationships']).difference(set(props['relationships']))}
                new_grouping[new_key] = {'props' : new_props, 'relationships' : new_relationships}
            else:
                new_grouping[key] = grouping[key]

        return new_grouping


    def intersect_props_relationships(self, grouping, intersections):
        aux_key = (next(iter(intersections)), 'node')
        new_props = grouping[aux_key]['props']
        new_relationships = grouping[aux_key]['relationships']
        for label in intersections:
            new_props = {k : grouping[aux_key]['props'][k] for k in set(new_props).intersection(set(grouping[(label, 'node')]['props']))}
            new_relationships = {k : grouping[aux_key]['relationships'][k] for k in set(new_relationships).intersection(set(grouping[(label, 'node')]['relationships']))}

        return {'props' : new_props, 'relationships' : new_relationships}


    def extract(self):
        grouping_nodes = self._collator.grouping_nodes()
        print('\n -------- Groupings -------- \n')
        SchemaExtractor.print_grouping_nodes(grouping_nodes)

        unique_labels_processed = dict()
        iteration = 0

        labels_to_process = True
        while labels_to_process:
            print('\n -------- ITERATION ' + str(iteration) + ' --------')
            iteration += 1
            labels_to_process = False
            grouping_nodes.pop((frozenset(), 'node'), None)
                
            labels_combinations = {k[0] for k in grouping_nodes.keys()}
            print('\nLabels combinations:' + str(labels_combinations))
            SchemaExtractor.print_grouping_nodes(unique_labels_processed)
       
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

                    print('\nKey with most intersections: ' + str(key_with_most_intersections))
                    print('Intersections: ' + str(intersections[key_with_most_intersections]))
                    unique_labels_processed[key_with_most_intersections] = self.intersect_props_relationships(
                                                                            grouping_nodes, 
                                                                            intersections[key_with_most_intersections])

                    grouping_nodes = self.process_intersection(grouping_nodes, 
                                                               key_with_most_intersections, 
                                                               unique_labels_processed[key_with_most_intersections])

        if len(grouping_nodes) > 0:
            print('!!!!! ----- Intersection was not enough! ----- !!!!!')
            # TODO Can be done the difference too after the 'if len(intersections) > 0:' in a else statement
            for k in grouping_nodes:
                print('WTF: ' + str(k))
                unique_labels_processed[k] = grouping_nodes[k]
    
        return {**unique_labels_processed, **self._collator.grouping_relationships()}


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
    grouping = schema.extract()
    SchemaExtractor.print_grouping_nodes(grouping)
