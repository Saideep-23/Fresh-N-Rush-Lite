from flask import Flask, g
from applications.database import close_db

app = Flask(__name__)
app.secret_key = 'secret'
app.app_context().push()

@app.teardown_appcontext
def teardown_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()



from applications.controllers import *
from applications.manager_controller import *


if __name__ == '__main__':
    app.run(debug=True)
