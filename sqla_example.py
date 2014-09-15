from eve import Eve
from eve.io.sql import SQL, ValidatorSQL
from tables import Base

app = Eve(validator=ValidatorSQL, data=SQL)

# bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

# Insert some example data in the db
#if not db.session.query(Address).count():
#    import example_data
#    for item in example_data.test_data:
#        db.session.add(Address.from_tuple(item))
#    db.session.commit()

app.run(debug=True, use_reloader=True) # using reloaded will destroy db
