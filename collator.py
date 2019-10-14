from database import Database
from itertools import chain, combinations

class Collator():
    # The first part of the algorithm, The Collator:
    # 1. Check all node labels combinations
    # 2. Gather all properties and relationships from those labels combinations
    #    organizing in a dictionary
    #    grouping_nodes method
    #
    #    key:   (labels, number of nodes)
    #    value: a dictionary with two entries that are also dictionaries 
    # 
    #       keys: 'props' and 'relationships
    #
    #               key:    (property name, property type)
    #               value:  number of ocurrences
    #
    #               key:    (relationship type, set of nodes labels)
    #               value:  a boolean that says if this relationship appears in all
    #                       nodes os not
    # 
    # 3. Gather all relationships and its properties and organize in a similar way:
    #    grouping_relationships method
    #    
    #    key:   (labels, number of nodes)
    #    value: another dictionary with -> key: (property name, property type)
    #                                      value: number of appearences
    #
    # 4. The dictionary from the grouping_relationships method (step 3) is ready
    #    to be parsed into the JSON-Schema, but the dictionary from the grouping_nodes 
    #    (step 2) method still needs some adjustments because of the multi label that 
    #    is allowed for nodes, this is done in the SchemaExtractor

    # TODO REMOVE THE PRINTINGS WHEN ITS DONE

    def __init__(self, database):
        self._database = database


    def grouping_nodes(self):
        labels_powerset = self._get_labels_combination(self._database.get_labels())
        grouping = dict()
        for label_combination in labels_powerset:
            records = [r for r in self._database.get_nodes_by_labels(label_combination)]
            if len(records) == 0:
                continue

            key = (label_combination, len(records))
            grouping[key] = dict()
            print('\nLabel combination: ' + str(label_combination))
            print('Size: ' + str(len(records)))
            for record in records:
                self._process_props_grouping(grouping, key, record, 'node')
                self._process_relationships_grouping(grouping, key, record['node'].id)

        self._check_mandatory_props(grouping)
        return self._process_keys(grouping, 'node')

    
    def grouping_relationships(self):
        types = self._database.get_relationship_types()
        grouping = dict()
        for typed in types:
            records = [r for r in self._database.get_relationships_by_type(typed)]
            if len(records) == 0:
                continue

            key = (typed, len(records))
            grouping[key] = dict()
            print('\nRelationship type: ' + str(typed))
            print('Size: ' + str(len(records)))
            for record in records:
                self._process_props_grouping(grouping, key, record, 'relationship')

        self._check_mandatory_props(grouping)
        return self._process_keys(grouping, 'relationship')


    def _process_props_grouping(self, grouping, key, record, record_name):
        # Adds how many times a prop was found in the nodes or relationships with the same labels
        if 'props' not in grouping[key].keys():
            grouping[key]['props'] = dict()

        for prop in record[record_name].keys():
            typed = type(record[record_name].get(prop))
            prop_key = (prop, typed)
            if prop_key in grouping[key]['props'].keys():
                grouping[key]['props'][prop_key] = grouping[key]['props'][prop_key] + 1
            else:
                grouping[key]['props'][prop_key] = 1


    def _process_relationships_grouping(self, grouping, key, node_id):
        # Gathers all relationships that flow out nodes with certain label
        # Checks if that realtionship is present in every node from that label or not
        relationships = self._database.get_relationships_types_by_id(node_id)
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


    def _check_mandatory_props(self, grouping):
        # Checks if a certain property is mandatory
        for key in grouping:
            size = key[1]
            for prop in grouping[key]['props']:
                if grouping[key]['props'][prop] == size:
                    grouping[key]['props'][prop] = True
                else:
                    grouping[key]['props'][prop] = False

    
    def _process_keys(self, grouping, new_key_name):
        # Removes the size from the key name
        processed_grouping = dict()
        for key in grouping:
            processed_grouping[(key[0], new_key_name)] = grouping[key]

        return processed_grouping


    def _get_labels_combination(self, labels):
        return self._powerset(labels)

        
    def _powerset(self, iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        tuples = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
        return filter(None, map(frozenset, tuples))
