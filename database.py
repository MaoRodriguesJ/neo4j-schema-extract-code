from driver import Driver
from query import Query

class Database():
    # A class to use the driver abstraction and execute the queries needed to the extraction
    # The explanation for each query can be found in the Query file

    def __init__(self, driver):
        self._driver = driver


    def get_labels(self):
        return [l['label'] for l in self._driver.read_transaction(Query._get_labels)]


    def get_relationship_types(self):
        return [t['relationshipType'] for t in self._driver.read_transaction(Query._get_types)]


    def get_nodes_by_labels(self, labels):
        params = {}
        for index, value in enumerate(labels):
            params['label' + str(index)] = value
        
        return self._driver.read_transaction(Query._get_nodes_by_label, params)

    
    def get_relationships_types_by_id(self, node_id):
        params = {'id' : node_id}
        return self._driver.read_transaction(Query._get_relationships_types_by_id, params)

    
    def get_relationships_by_type(self, typed):
        params = {'type': typed}
        return self._driver.read_transaction(Query._get_relationships_by_type, params)
