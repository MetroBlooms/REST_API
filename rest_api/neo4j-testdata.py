from py2neo import Graph, Path,  neo4j, node, rel, authenticate, Relationship

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, RelationshipFrom)

# auth for py2neo
# set URL and credentials as per your own local setup
authenticate("localhost:7474","neo4j","")
gdb = neo4j.Graph("http://localhost:7474/db/data")

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
ScoreCard = models.ScoreCard
Neighborhood = models.Neighborhood

# Create 3 addresses
# Place 3 sites in each address with a geolocation on each site
# Create 3 evaluations for each site
# Create 10 scorecards for each evaluation
for NaberI in range(1,4):
    strNaber = str(NaberI)
    theNaber = Neighborhood(name='Neighborhood '+strNaber).save()
    for AddrI in range(1,4):
        strAddrI = str(AddrI)
        theAddr = Address(address='Street'+strAddrI,city='Minneapolis',state='MN',zipcode='5542'+strAddrI).save()
        theNaber.address.connect(theAddr)
        for siteI in range(1,4):
            strSiteI = str(siteI)
            theSite = Site(name="Site"+strAddrI+strSiteI).save()
            thePosition = Geoposition(latitude='111.'+strSiteI,longitude='222.'+strSiteI,accuracy='1',timestamp='Mar-'+strSiteI+'-2016').save()
            theAddr.site.connect(theSite)
            thePosition.site.connect(theSite)
            for evalI in range(1,4):
                strEvalI = str(evalI)
                theEval = Evaluation(evaluator_id=strEvalI, evaluator='Evaluator'+strEvalI, exists='True', evaluated_when='Mar-'+strEvalI+'-2016', comment='testing 123...').save()
                theSite.evaluation.connect(theEval)
                for scoreI in range(1,11):
                    strScoreI = str(scoreI)
                    scorecard = ScoreCard(factor_type="FactorType"+strScoreI,score=scoreI).save()
                    scorecard.site.connect(theEval)


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
