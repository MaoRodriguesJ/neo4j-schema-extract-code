from neo4j.v1 import GraphDatabase

class Driver():

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def read_transaction(self, query, parameters):
        with self._driver.session() as session:
            return session.read_transaction(query, parameters)

    def write_transaction(self, query, parameters):
        with self._driver.session() as session:
            return session.write_transaction(query, parameters)