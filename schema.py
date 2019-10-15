from collator import Collator
from database import Database
from driver import Driver
from extractor import Extractor
from parser import Parser
import sys

class Schema():

    def __init__(self, database):
        self._collator = Collator(database)
        self._extractor = Extractor()
        self._parser = Parser()

    def generate(self, path):
        print(' ---- Path to generate file: ' + str(path) + ' ---- ')

        grouping_nodes = self._collator.grouping_nodes()
        grouping_relationships = self._collator.grouping_relationships()

        extracted_grouping_nodes = self._extractor.extract(grouping_nodes)

        parsed_list = self._parser.parse({**extracted_grouping_nodes, **grouping_relationships})

        print('\n ---- Done ----')
        Extractor.print_grouping_nodes(parsed_list)


if __name__ == '__main__':
    url = "bolt://0.0.0.0:7687"
    login = "neo4j"
    password = "neo4jadmin"
    path = "generated_schema"

    if len(sys.argv) == 5:
        url = sys.argv[1]
        login = sys.argv[2]
        password = sys.argv[3]
        path = sys.argv[4]
    
    if len(sys.argv) == 2:
        path = sys.argv[2]

    schema = Schema(Database(Driver(url, login, password)))
    schema.generate(path)
