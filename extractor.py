
class Extractor():
    # The second part of the algorithm, The Extractor
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
    #   The difference also not works when there are multiple multilabels that have the same diff in
    #   the labels, e.g {'User', 'Person'}, {'Actor', 'Person'}, {'Director', 'Person'}
    #   two differences that result in User only
    #
    # 2. With intersection its simple, find multilabel nodes that intersect forming only one
    #    label, intersect the properties and the relationships of those multilabel too to form
    #    a new entry in the dictionary that has only one label (intersect_props_relationships method), 
    #    than extract this label and its relationships and properties from those multilabel 
    #    (process_intersection method) and reapeat this process until only one label nodes rest or we dont 
    #    have any other options to infer how those left multilabel ones could be split

    def __init__(self):
        pass


    def extract(self, grouping):
        grouping_nodes = grouping

        unique_labels_processed = dict()
        labels_to_process = True

        while labels_to_process:
            labels_to_process = False
            grouping_nodes.pop((frozenset(), 'node'), None)
                
            labels_combinations = {k[0] for k in grouping_nodes.keys()}

            labels_len_1 = set()
            for label in labels_combinations:
                if len(label) == 1:
                    unique_labels_processed[label] = grouping_nodes.pop((label, 'node'))
                    labels_to_process = True
                    labels_len_1.add(label)

            if labels_to_process:
                for l in labels_len_1:
                    grouping_nodes = self._process_intersection(grouping_nodes, l, unique_labels_processed[l])

            else:
                intersections = self._get_labels_intersections(labels_combinations)
                if len(intersections) > 0:
                    labels_to_process = True
                    key_with_most_intersections = self._get_key_with_most_intersections(intersections)

                    unique_labels_processed[key_with_most_intersections] = self._intersect_props_relationships(
                                                                            grouping_nodes, 
                                                                            intersections[key_with_most_intersections],
                                                                            key_with_most_intersections)

                    grouping_nodes = self._process_intersection(grouping_nodes, 
                                                                key_with_most_intersections, 
                                                                unique_labels_processed[key_with_most_intersections])

        if len(grouping_nodes) > 0:
            for k in grouping_nodes:
                unique_labels_processed[k] = grouping_nodes[k]

        return unique_labels_processed


    def _process_intersection(self, grouping, label, props):
        # Retrocheck if with the current new unique labels (props) its possible to separate any multilabel node
        new_grouping = dict()
        for key in grouping:
            if key[0].intersection(label):
                new_key = (key[0].difference(label), 'node')
                new_props = {k : grouping[key]['props'][k] 
                             for k in set(grouping[key]['props']).difference(set(props['props']))}

                new_relationships = {k : grouping[key]['relationships'][k] 
                                     for k in set(grouping[key]['relationships']).difference(set(props['relationships']))}

                self._process_new_relationships(new_relationships, label)

                new_grouping[new_key] = {'props' : new_props, 'relationships' : new_relationships}
            else:
                new_grouping[key] = grouping[key]

        return new_grouping


    def _intersect_props_relationships(self, grouping, intersections, key):
        # Intersects props and relationships from all intersections found in the labels
        aux_key = (next(iter(intersections)), 'node')
        new_props = grouping[aux_key]['props']
        new_relationships = grouping[aux_key]['relationships']
        for label in intersections:
            new_props = {k : grouping[aux_key]['props'][k] 
                         for k in set(new_props).intersection(set(grouping[(label, 'node')]['props']))}

            new_relationships = {k : grouping[aux_key]['relationships'][k] 
                                 for k in set(new_relationships).intersection(set(grouping[(label, 'node')]['relationships']))}

        self._process_new_relationships(new_relationships, key)

        return {'props' : new_props, 'relationships' : new_relationships}


    def _process_new_relationships(self, new_relationships, key):
        # Since we found an intersection we need to remove from the relationships that had a multilabel node
        old_relationships = list()
        for relationship in new_relationships:
            if len(relationship[1]) > 1 and next(iter(key)) in relationship[1]:
                old_relationships.append({relationship : new_relationships[relationship]})

        for relationship in old_relationships:
            for r in relationship:
                new_relationships.pop(r)
                new_relationships[(r[0], key)] = relationship[r]
                new_relationships[(r[0], r[1].difference(key))] = relationship[r]


    def _get_labels_intersections(self, labels_combinations):
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

        return intersections


    def _get_key_with_most_intersections(self, intersections):
        key_with_most_intersections = next(iter(intersections))
        for k in intersections:
            if len(intersections[k]) > len(intersections[key_with_most_intersections]):
                key_with_most_intersections = k
        
        return key_with_most_intersections
