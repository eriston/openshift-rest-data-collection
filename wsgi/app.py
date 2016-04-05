from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, render_template, jsonify, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
from flask.ext.httpauth import HTTPBasicAuth


app = Flask(__name__, static_url_path="")
api = Api(app)

app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

dataPoint_fields = {
    'id': fields.Integer,
    'pub_date': fields.DateTime,
    'device_id': fields.String,
    'sensor_id': fields.String,
    'session_id': fields.Integer,
    'sensor_value': fields.Float,
    'sensor_timestamp': fields.Integer,
    'notes': fields.String,
}

class DataPoint(db.Model):
    __tablename__ = 'data_points'
    id = db.Column('id', db.Integer, primary_key=True)
    device_id = db.Column(db.String(60))
    sensor_id = db.Column(db.String(60))
    session_id = db.Column(db.Integer)
    sensor_value = db.Column(db.Float(precision=10))
    sensor_timestamp = db.Column(db.Integer)
    pub_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    def __init__(self, device_id, session_id, sensor_id, sensor_value, sensor_timestamp, notes):
        self.device_id = device_id
        self.sensor_id = sensor_id
        self.session_id = session_id
        self.sensor_value = sensor_value
        self.sensor_timestamp = sensor_timestamp
        self.pub_date = datetime.utcnow()
        self.notes = notes

@app.route('/')
def index():
    return render_template('index.html',
        datpts=DataPoint.query.order_by(DataPoint.pub_date.desc()).all()
    )


parser = reqparse.RequestParser()
parser.add_argument('sensor_id', type=str, required=True, help='missing sensor_id', location='json')
parser.add_argument('sensor_value', type=float, required=True, help='missing sensor_value', location='json')
parser.add_argument('sensor_timestamp', type=int, required=True, help='missing sensor_timestamp', location='json')
parser.add_argument('device_id', type=str, required=True, help='missing device_id', location='json')
parser.add_argument('session_id', type=str, required=True, help='missing session_id', location='json')
parser.add_argument('notes', type=str, required=False, location='json')

class DataPointListAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        super(DataPointListAPI, self).__init__()

    def get(self):
        datapoints1 = db.session.query(DataPoint).all()
        return {'datapoints': [marshal(dpoint, dataPoint_fields) for dpoint in datapoints1]}


    @marshal_with(dataPoint_fields)
    def post(self):
        args = parser.parse_args()
        datpnt = DataPoint(args['device_id'], \
            args['session_id'],args['sensor_id'],args['sensor_value'], \
            args['sensor_timestamp'], args['notes'])
        db.session.add(datpnt)
        db.session.commit()
        return datpnt, 201


api.add_resource(DataPointListAPI, '/wearables/api/v2/datapoints', endpoint='datapoint')


if __name__ == '__main__':
    app.run()
