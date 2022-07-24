from crypt import methods
from werkzeug.exceptions import HTTPException
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=["GET"])
@requires_auth("get:drinks")
def get_drinks(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
    except:
        abort(404)

    return jsonify({"success": True, "drinks": [drink.short() for drink in drinks]}), 200


@ app.route('/drinks-detail', methods=["GET"])
@ requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()

    except:
        abort(404)

    return jsonify({"success": True, "drinks": [drink.long() for drink in drinks]}), 200


@ app.route('/drinks', methods=["POST"])
@ requires_auth("post:drinks")
def create_drink(payload):
    body = request.get_json()

    try:
        title = body.get("title", None)
        recipe = body.get("recipe", None)

        if type(recipe) is dict:
            recipe = [recipe]

        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )

        drink.insert()

    except:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})


@ app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@ requires_auth("patch:drinks")
def update_drink(payload, drink_id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink:
        abort(404)

    try:
        title = body.get('title', None)

        if title:
            drink.title = title

        drink.update()
    except:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@ app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@ requires_auth("post:drinks")
def delete_drink(payload, drink_id):
    # print("===>>", payload)
    return "Drinks successfully deleted."


# Error Handling

@ app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@ app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404,
                "message": "resource not found"}),
        404,
    )


@ app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


@ app.errorhandler(405)
def not_allowed(error):
    return jsonify({"success": False, "error": 405, "message": "method not allowed"}), 405


@ app.errorhandler(401)
def unauthorized(error):
    return jsonify({"success": False, "error": 401, "message": "unauthorized"}), 401


@ app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": 500, "message": "internal server error"}), 500


@ app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@ app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response
