#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        # Validate presence
        if not username or not password:
            return make_response({"error": "Unprocessable Entity"}, 422)

        try:
            user = User(
                username=username,
                bio=data.get("bio"),
                image_url=data.get("image_url"),
            )
            user.password_hash = password

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            return make_response(user.to_dict(), 201)

        except IntegrityError:
            db.session.rollback()
            return make_response({"error": "Unprocessable Entity"}, 422)



class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return make_response(user.to_dict(), 200)
        return make_response({"error": "Unauthorized"}, 401)


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return make_response(user.to_dict(), 200)

        return make_response({"error": "Invalid username or password"}, 401)


class Logout(Resource):
    def delete(self):
        user_id =session.get("user_id")

        if not user_id:
            return make_response({"error": "Unauthorized"}, 401)
        

        session["user_id"] = None
        return make_response({}, 204)

class RecipeIndex(Resource):
    def get(self):
        """Return all recipes for the logged-in user."""
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = db.session.get(User, user_id)
        if not user:
            return {"error": "User not found"}, 404

        recipes = [r.to_dict() for r in user.recipes]
        return recipes, 200

    def post(self):
        """Create a new recipe for the logged-in user."""
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        # Validate required fields
        if not data or not data.get("title") or not data.get("instructions") or not data.get("minutes_to_complete"):
            return {"error": "Invalid recipe"}, 422

        try:
            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=int(data["minutes_to_complete"]),
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201

        except (IntegrityError, ValueError, TypeError):
            db.session.rollback()
            return {"error": "Invalid recipe"}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)