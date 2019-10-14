from neo4j.v1 import GraphDatabase

class Driver():
    # Driver abstraction used to access the Neo4j database
    # With read and write transactions that can be parametized

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def read_transaction(self, query, parameters=None):
        with self._driver.session() as session:
            if parameters:
                return session.read_transaction(query, parameters)
            
            return session.read_transaction(query)


    def write_transaction(self, query, parameters=None):
        with self._driver.session() as session:
            if parameters:
                return session.write_transaction(query, parameters)

            return session.write_transaction(query)
