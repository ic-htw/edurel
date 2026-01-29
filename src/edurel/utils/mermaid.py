import yaml
from pathlib import Path
from typing import List


class ERDiagram:
    """Class for converting ER diagrams from YAML format to Mermaid syntax.

    The ER model should contain the following optional keys:
    - entities: List of entity definitions
    - associative_entities: List of associative entity definitions
    - relationships: List of relationship definitions
    - inheritances: List of inheritance hierarchies
    - valuelists: List of valuelist definitions
    """

    def __init__(self, ermodel: str):
        """Initialize ERDiagram with YAML string.

        Args:
            ermodel: YAML string containing the ER model
        """
        self.ermodel = ermodel
        self.schema = yaml.safe_load(ermodel)

    @classmethod
    def from_string(cls, model_str: str) -> 'ERDiagram':
        """Factory method to create ERDiagram from YAML string.

        Args:
            model_str: YAML string containing the ER model

        Returns:
            ERDiagram instance
        """
        return cls(model_str)

    @classmethod
    def from_file(cls, file_path: str) -> 'ERDiagram':
        """Factory method to create ERDiagram from file path.

        Args:
            file_path: Path to YAML file containing the ER model

        Returns:
            ERDiagram instance
        """
        with open(file_path, 'r') as f:
            model_str = f.read()
        return cls(model_str)

    def toMermaid(self) -> str:
        """Convert ER diagram to Mermaid ER diagram syntax.

        Returns:
            str: Mermaid ER diagram code
        """
        lines = ["erDiagram"]
        lines.extend(self._process_entities())
        lines.extend(self._process_valuelists())
        lines.extend(self._process_associative_entities())
        lines.extend(self._process_associative_relationships())
        lines.extend(self._process_relationships())
        lines.extend(self._process_inheritances())
        return "\n".join(lines)

    def _cardinality_to_mermaid(self, card: str) -> str:
        """Convert cardinality notation to Mermaid symbols.

        Args:
            card: ONE, MANY, OPTIONAL_ONE, or OPTIONAL_MANY

        Returns:
            str: Mermaid cardinality symbol (||, |o, }|, }o)
        """
        mapping = {
            'ONE': '||',
            'MANY': '}|',
            'OPTIONAL_ONE': '|o',
            'OPTIONAL_MANY': '}o'
        }
        return mapping.get(card, '||')

    def _process_entities(self) -> List[str]:
        """Process regular entities into Mermaid entity definitions.

        Returns:
            List of Mermaid entity definition lines
        """
        lines = []
        entities = self.schema.get('entities', [])

        for entity in entities:
            entity_name = entity['entityname']
            key = entity.get('key')
            attributes = entity.get('attributes', [])

            lines.append(f"    {entity_name} {{")

            # Add key as PK
            if key:
                lines.append(f"        string {key} PK")

            # Add attributes
            for attr in attributes:
                attr_name = attr['attributename']
                attr_type = attr['type']
                lines.append(f"        {attr_type} {attr_name}")

            lines.append("    }")

        return lines

    def _process_valuelists(self) -> List[str]:
        """Process valuelists into Mermaid entity definitions.

        Valuelists are represented as entities with standard fields.

        Returns:
            List of Mermaid entity definition lines
        """
        lines = []
        valuelists = self.schema.get('valuelists', [])

        for vl in valuelists:
            vl_name = vl['valuelistname']
            lines.append(f"    {vl_name} {{")
            lines.append("        INTEGER ID PK")
            lines.append("        TEXT Description")
            lines.append("        BOOLEAN IsValid")
            lines.append("        INTEGER SortOrder")
            lines.append("    }")

        return lines

    def _process_associative_entities(self) -> List[str]:
        """Process associative entities into Mermaid entity definitions.

        Returns:
            List of Mermaid entity definition lines
        """
        lines = []
        associative_entities = self.schema.get('associative_entities', [])

        for ae in associative_entities:
            ae_name = ae['associationname']
            key = ae.get('key')
            attributes = ae.get('attributes', [])

            lines.append(f"    {ae_name} {{")

            # Add key as PK if present
            if key:
                lines.append(f"        string {key} PK")

            # Add attributes
            for attr in attributes:
                attr_name = attr['attributename']
                attr_type = attr['type']
                lines.append(f"        {attr_type} {attr_name}")

            lines.append("    }")

        return lines

    def _process_associative_relationships(self) -> List[str]:
        """Process relationships from associative entities.

        Returns:
            List of Mermaid relationship lines
        """
        lines = []
        associative_entities = self.schema.get('associative_entities', [])

        for ae in associative_entities:
            ae_name = ae['associationname']

            # Process associations
            associations = ae.get('associations', [])
            for assoc in associations:
                target = assoc['targetentity']
                role = assoc.get('role', target)
                card = assoc.get('cardinality', 'ONE')

                # Associative entity to target entity
                card_symbol = self._cardinality_to_mermaid(card)
                lines.append(f"    {ae_name} }}o--{card_symbol} {target} : \"{role}\"")

            # Process identified_by relationships
            identified_by = ae.get('identified_by', [])
            for ident in identified_by:
                target = ident['targetentity']
                card = ident.get('cardinality', 'ONE')
                card_symbol = self._cardinality_to_mermaid(card)
                lines.append(f"    {ae_name} }}|--{card_symbol} {target} : \"identified by\"")

        return lines

    def _process_relationships(self) -> List[str]:
        """Process regular relationships between entities.

        Returns:
            List of Mermaid relationship lines
        """
        lines = []
        relationships = self.schema.get('relationships', [])

        for rel in relationships:
            rel_name = rel['relationshipname']
            entities_list = rel.get('entities', [])
            cardinality = rel.get('cardinality', {})

            if len(entities_list) == 2:
                entity1 = entities_list[0]
                entity2 = entities_list[1]

                entity1_name = entity1['entityname']
                entity2_name = entity2['entityname']

                role1 = entity1.get('role', entity1_name)
                role2 = entity2.get('role', entity2_name)

                # Get cardinalities (default to ONE if not specified)
                card1 = cardinality.get(role1, 'ONE')
                card2 = cardinality.get(role2, 'ONE')

                # Build relationship line
                card1_symbol = self._cardinality_to_mermaid(card1)
                card2_symbol = self._cardinality_to_mermaid(card2)

                lines.append(f"    {entity1_name} {card1_symbol}--{card2_symbol} {entity2_name} : \"{rel_name}\"")

        return lines

    def _process_inheritances(self) -> List[str]:
        """Process inheritance hierarchies.

        Inheritance is represented as relationships in Mermaid.

        Returns:
            List of Mermaid relationship lines
        """
        lines = []
        inheritances = self.schema.get('inheritances', [])

        for inh in inheritances:
            super_entity = inh['superentity']
            sub_entities = inh.get('subentities', [])

            for sub in sub_entities:
                # Represent inheritance as a relationship
                lines.append(f"    {sub} ||--|| {super_entity} : \"inherits from\"")

        return lines
