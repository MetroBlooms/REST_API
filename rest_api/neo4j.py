from py2neo import Graph, Path,  neo4j, node, rel, authenticate, Relationship

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, RelationshipFrom)

import neo4j_models as models

# TODO: set as environment variable for consumption by neomodel
# at command prompt 'export NEO4J_REST_URL=http://neo4j:bippy@iznej.local:7474/db/data/'
# note that iznej.local is the URL to my local instance of neo4j
# --->
# below solution does not work. need to figure this out!!!
#import os
#os.system("export NEO4J_REST_URL=http://neo4j:bippy@iznej.local:7474/db/data/")

# Classes used in testing
Evaluation = models.Evaluation
Address = models.Address
Site = models.Site
Geoposition = models.Geoposition
Evaluation = models.Evaluation


# auth for py2neo
# set URL and credentials as per your own local setup
authenticate("iznej.local:7474", "neo4j", "bippy")
gdb = neo4j.Graph("http://iznej.local:7474/db/data/")

# create model instance
home = Address(address='1112 Stufflebeams Road', city='Saintly Park', state = 'MN', zipcode = '55466').save()

addresses = Address.create(
    {'address':'1218 N Oak Lane','city':'The Park','state':'MN','zipcode': '55411'},
    {'address':'2900 Winifred Ave N','city':'Gorden Volley','state':'MN','zipcode':'55433'}
)

# link address to site
grenzi = Site(name='Grenzi2').save()
home.site.connect(grenzi)

# link geolocale to site
here = Geoposition(latitude='123.456', longitude='789.101112', accuracy = '2', timestamp = 'now').save()
here.site.connect(grenzi)

# link site to evaluation
inspection = Evaluation(evaluator_id='123', evaluator= 'me', exists='True', evaluated_when='now', comment='testing 123...').save()
grenzi.evaluation.connect(inspection)

if home.site.is_connected(grenzi):
    print("Grez and Nez are Grenzi")

for s in grenzi.address.all():
    print(s.address)

len(grenzi.address)
print grenzi.name

# return site name
grenzi.address.search(address='1112 Stufflebeams Road')

#home.site.disconnect(grenzi)


#py2neo test
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


