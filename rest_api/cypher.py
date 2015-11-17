from py2neo import Graph, Path,  neo4j, node, rel, authenticate, Relationship

authenticate("iznej.local:7474", "neo4j", "bippy")
gdb = neo4j.Graph("http://iznej.local:7474/db/data/")

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
# only if they do not exist -> good for keying uniqueness
t = gdb.merge_one("Address","address","1234 N Oak Ln")
t['zipcode'] = '55466'
t['state'] = 'MN'
t.push()

u = gdb.merge_one("Site","name","Grenzi")
u.push()

# ensure that relationship is not recreated
gdb.create_unique(Relationship(t, "managedBy", u))
#MATCH (n { zipcode: '55422' })
#SET n :Address
#RETURN n

#MATCH (a:Site { sites: 'The Mothra' }), (b:Address { zipcode: '55422' })
# CREATE (a)-[:is_at]->(b)


