from py2neo import Graph, Path,  neo4j, node, rel, authenticate, Relationship

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, RelationshipFrom)

#import os
#os.system("export NEO4J_REST_URL=http://neo4j:bippy@iznej.local:7474/db/data/")


authenticate("iznej.local:7474", "neo4j", "bippy")
gdb = neo4j.Graph("http://iznej.local:7474/db/data/")

#neomodel test
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



grez_nez = Address(address='1112 Stufflebeams Road', city='Saintly Pork', state = 'MN', zipcode = '55466').save()

addresses = Address.create(
    {'address':'1218 N Oak Lane','city':'The Pork','state':'MN','zipcode': '55411'},
    {'address':'2900 Winifred Ave N','city':'Gorden Volley','state':'MN','zipcode':'55433'}
)

# link address to site
grenzi = Site(name='Grenzi2').save()
grez_nez.site.connect(grenzi)

# link geolocale to site
here = Geoposition(latitude='123.456', longitude='789.101112', accuracy = '2', timestamp = 'now').save()
here.site.connect(grenzi)

# link site to evaluation
good_site = Evaluation(evaluator_id='123', evaluator= 'me', exists='True', evaluated_when='now', comment='testing 123...').save()
grenzi.evaluation.connect(good_site)


if grez_nez.site.is_connected(grenzi):
    print("Grez and Nez are Grenzi")

for s in grenzi.address.all():
    print(s.address) # Jim

len(grenzi.address) # 1
print grenzi.name

# Find people called 'Jim' in germany
grenzi.address.search(address='1112 Stufflebeams Road')

#grez_nez.site.disconnect(grenzi)


#FOREACH (addresses IN [{'address':'1218 N Oak Lane','city':'The Pork','state':'MN','zipcode': '55411'}, {'address':'2900 Winifred Ave N','city':'Gorden Volley','state':'MN','zipcode':'55433'}]|
#         CREATE ({ address:addresses.address,city:addresses.city,state:addresses.state,zipcode:addresses.zipcode }))

#FOREACH (sites IN [{siteId:1,siteName:'The Mothra'}, {siteId:2,siteName:'Grenzi'}]|
#
#         CREATE ({ sites:sites.siteId,sites:sites.siteName}))

# create unique index
#gdb.schema.create_uniqueness_constraint("Site", "name")
#gdb.schema.create_uniqueness_constraint("Address","id")

# create multiple nodes
#sites = gdb.create(
#    {"name": "Grenzi1"}, {"name": "Mothra1"}
#)

#py2neo test
# create multiple nodes
# addresses = gdb.merge(
#     {'address':'1218 N Oak Lane','city':'The Pork','state':'MN','zipcode': '55411'},
#     {'address':'2900 Winifred Ave N','city':'Gorden Volley','state':'MN','zipcode':'55433'}
# )
#
# # only if they do not exist -> good for keying uniqueness
# t = gdb.merge_one("Address","address","2900 Winifred Ave N')
# t['zipcode'] = '55433'
# t['state'] = 'MN'
# t.push()
#
# u = gdb.merge_one("Site","name","Grenzi")
# u.push()
#
# # ensure that relationship is not recreated
# gdb.create_unique(Relationship(t, "managedBy", u))
# #MATCH (n { zipcode: '55418' })
#SET n :Address
#RETURN n

#MATCH (a:Site { sites: 'The Mothra' }), (b:Address { zipcode: '55433' })
# CREATE (a)-[:is_at]->(b)


