from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
cors = CORS(app,resources={
    r"/*":{
        "origins":"*"
    }
})

app.config['SQLALCHEMY_DATABASE_URI']='mysql://b0d32905800d16:04382c58@us-cdbr-east-03.cleardb.com/heroku_062f30bebe07508'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from main import routes