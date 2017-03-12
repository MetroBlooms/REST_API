"""

        neo4j model declarations

"""

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, RelationshipFrom)

#neomodel test
class Neighborhood(StructuredNode):
    name=StringProperty(unique_index=False,required=False)

    address = RelationshipFrom('Address', 'LOCATED_IN')

class ScoreCard(StructuredNode):
    factor_type = StringProperty(unique_index=False, required=True)#("garden", "rain garden", "permeable pavers")
    score = IntegerProperty(unique_index=False, required=True)

    site = RelationshipFrom('Evaluation', 'IS_SCORED')

class Evaluation(StructuredNode):
    type = StringProperty(unique_index=False, required=False)#("garden", "rain garden", "permeable pavers")
    evaluator_id = IntegerProperty(unique_index=False, required=True)
    evaluator = StringProperty(unique_index=False, required=True)
    evaluated_when = StringProperty(unique_index=False, required=True)
    exists = StringProperty(unique_index=False, required=True)
    comments = StringProperty(unique_index=False, required=False)

    site = RelationshipFrom('Site', 'IS_EVALUATED')
    score_card = RelationshipTo(ScoreCard, 'IS_SCORED')

class Site(StructuredNode):
    #id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(unique_index=False, required=True)

    # traverse incoming IS_FROM relation, inflate to Person objects
    address = RelationshipFrom('Address', 'IS_NAMED')
    geolocation = RelationshipFrom('Geoposition', 'HAS_COORDINATES')
    evaluation = RelationshipTo(Evaluation, 'IS_EVALUATED')

class Address(StructuredNode):
    #id = IntegerProperty(unique_index=True, required=True)
    address = StringProperty(unique_index=False, required=True)
    city = StringProperty(unique_index=False, required=True)
    state = StringProperty(unique_index=False, required=True)
    zipcode = StringProperty(unique_index=False, required=True)
    neighborhood = StringProperty(unique_index=False, required =False)
    county = StringProperty(unique_index=False, required=False)

    # traverse outgoing IS_FROM relations, inflate to Country objects
    site = RelationshipTo(Site, 'IS_NAMED')

class Geoposition(StructuredNode):
    #id = IntegerProperty(unique_index=True, required=True)
    latitude = StringProperty(unique_index=False, required=True)
    longitude = StringProperty(unique_index=False, required=True)
    accuracy = StringProperty(unique_index=False, required=True)
    timestamp = StringProperty(unique_index=False, required=True)

    site = RelationshipTo(Site, 'HAS_COORDINATES')
