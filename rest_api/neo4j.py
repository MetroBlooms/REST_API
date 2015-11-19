from py2neo import Graph, Path,  neo4j, node, rel, authenticate, Relationship

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, RelationshipFrom)

from app import app, models


# TODO: set as environment variable for consumption by neomodel
#import os
#os.system("export NEO4J_REST_URL=http://neo4j:bippy@iznej.local:7474/db/data/")

# Classes used in testing
Evaluation = models.Evaluation
Address = models.Address
Site = models.Site
Geoposition = models.Geoposition
Evaluation = models.Evaluation


authenticate("iznej.local:7474", "neo4j", "bippy")
gdb = neo4j.Graph("http://iznej.local:7474/db/data/")


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


