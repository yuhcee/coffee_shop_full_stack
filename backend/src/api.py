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

    if drink is None:
        abort(404)

    try:
        title = body.get('title', None)

        if title:
            drink.title = title

        drink.update()
    except:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200


@ app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@ requires_auth("post:drinks")
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
    except:
        abort(400)

    return jsonify({'success': True, 'delete': drink_id}), 200


# Error Handling

@ app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(403)
def permission_not_found(error):
    return jsonify({"success": False, "error": 403, "message": "permission not found"}), 403


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
