
class Parser():
    # The Parser maps to json-schema files the extracted nodes and relationships

    def __init__(self):
        pass


    def parse(self, grouping_nodes, grouping_relationships):
        parsed_list = list()
        for key in grouping_relationships.keys():
            parsed_list.append(self._parse_relationship(key, grouping_relationships[key]['props']))

        for key in grouping_nodes.keys():
            parsed_list.append(self._parse_node(key, grouping_nodes[key]))
        
        return parsed_list

    
    def _parse_node(self, key, node):
        parsed_node = dict()
        parsed_node["$schema"] = "https://json-schema.org/draft/2019-09/schema#"
        parsed_node["$id"] = self._build_node_id(key) + '.json'
        parsed_node["definitions"] = dict()
        parsed_node["type"] = "object"
        parsed_node["properties"] = dict()
        parsed_node["required"] = list()
        parsed_node["additionalProperties"] = False

        for key in node['props']:
            typed = self._check_type(key[1])
            parsed_node["properties"][key[0]] = {"type" : typed}
            if node['props']:
                parsed_node["required"].append(key[0])

        if len(node['relationships']) > 0:
            parsed_node["properties"]["relationships"] = dict()
            parsed_node["properties"]["relationships"]["type"] = "array"
            parsed_node["properties"]["relationships"]["items"] = dict()
            parsed_node["properties"]["relationships"]["items"]["oneOf"] = list()

            relationship_required = False
            for key in node['relationships']:
                new_relationship = dict()
                new_relationship["type"] = "array"
                new_relationship["items"] = list()

                relationship_id = str(key[0]).lower()
                node_id = self._build_node_id(key[1])

                relationship_type = dict()
                relationship_type["type"] = "object"
                relationship_type["$ref"] = "#/definitions/" + relationship_id
                new_relationship["items"].append(relationship_type)

                node_type = dict()
                node_type["type"] = "object"
                node_type["$ref"] = "#/definitions/" + node_id
                new_relationship["items"].append(node_type)

                parsed_node["definitions"][relationship_id] = dict()
                parsed_node["definitions"][relationship_id]["type"] = "object"
                parsed_node["definitions"][relationship_id]["$ref"] = relationship_id + '.json'

                parsed_node["definitions"][node_id] = dict()
                parsed_node["definitions"][node_id]["type"] = "object"
                parsed_node["definitions"][node_id]["$ref"] = node_id + '.json'

                parsed_node["properties"]["relationships"]["items"]["oneOf"].append(new_relationship)

                if not relationship_required and node['relationships'][key]:
                    relationship_required = True
                    parsed_node["required"].append("relationships")

        return parsed_node


    def _parse_relationship(self, key, props):
        parsed_relationship = dict()
        parsed_relationship["$schema"] = "https://json-schema.org/draft/2019-09/schema#"
        parsed_relationship["$id"] = str(key[0]).lower() + '.json'
        parsed_relationship["type"] = "object"
        parsed_relationship["properties"] = dict()
        parsed_relationship["required"] = list()
        parsed_relationship["additionalProperties"] = False

        for key in props:
            typed = self._check_type(key[1])
            parsed_relationship["properties"][key[0]] = {"type" : typed}
            if props[key]:
                parsed_relationship["required"].append(key[0])

        return parsed_relationship

    
    def _check_type(self, typed):
        if typed is str:
            return "string"
        
        if typed is int or typed is float:
            return "number"

        if typed is dict:
            return "object"

        if typed is list:
            return "array"

        if typed is bool:
            return "boolean"

        else:
            return typed

    
    def _build_node_id(self, key):
        id_name = ''
        for label in key:
            id_name += '_' + str(label).lower()
            
        return id_name[1:]
