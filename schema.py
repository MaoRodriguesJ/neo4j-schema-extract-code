from collator import Collator
from database import Database
from driver import Driver
from extractor import Extractor
from parser import Parser
from pathlib import Path
import sys, os, json

class Schema():
    # Schema get the input from the Collator and the Extractor to feed the Parser
    # and generate a list of ready json files to be saved

    def __init__(self, database):
        self._collator = Collator(database)
        self._extractor = Extractor()
        self._parser = Parser()

    def generate(self, path):
        grouping_nodes = self._collator.grouping_nodes()
        print('\n ---- Done Grouping Nodes ----')
        Schema.print_grouping(grouping_nodes)

        grouping_relationships = self._collator.grouping_relationships()
        print('\n ---- Done Grouping Relationships ----')
        Schema.print_grouping(grouping_relationships)

        extracted_grouping_nodes = self._extractor.extract(grouping_nodes)

        print('\n ---- Done Extracting ----')
        Schema.print_grouping({**extracted_grouping_nodes, ** grouping_relationships})

        parsed_list = self._parser.parse(extracted_grouping_nodes, grouping_relationships)

        self._save(path, parsed_list)


    def _save(self, path, parsed_list):
        if not os.path.exists(path):
            os.makedirs(path)

        data_folder = Path(path)
        for item in parsed_list:
            with open(data_folder / item['$id'], 'w') as parsed_file:
                json.dump(item, parsed_file, indent=4)

    
    @staticmethod
    def print_grouping(grouping):
        for k in grouping:
            print('\nKey: ' + str(k))
            print('Properties: ' +str(grouping[k]['props']))
            if 'relationships' in grouping[k].keys():
                print('Relationships: ' + str(grouping[k]['relationships']))
            
            if 'allOf' in grouping[k].keys():
                print('allOf: ' + str(grouping[k]['allOf']))


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

    schema = Schema(Database(Driver(url, login, password)))
    schema.generate(path)
