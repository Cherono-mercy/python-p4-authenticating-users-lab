#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Login resource
class Login(Resource):
    # Has one route, post()
    def post(self):
        # post() gets a username from request's JSON and retrieves the user by username
        user = User.query.filter(
            User.username == request.get_json()['username']
        ).first()
        # post() sets the session's 'user_id' to the user's id
        session['user_id'] = user.id
        # post() returns the user as JSON with a 200 status code
        return user.to_dict(), 200

# Logout resource    
class Logout(Resource):
    # Has one route, delete()
    def delete(self):
        # delete() removes user_id value from the session
        session['user_id'] = None
        # delete() returns no data and a 204(No content) status code
        return {}, 204

# CheckSession resource located at '/check_session'
class CheckSession(Resource):
    # Has one route, get()
    def get(self):
        # get() retrieves the user_id value from the session
        user = User.query.filter(User.id == session.get('user_id')).first()
        # If the session has a user_id, get() returns the user as JSON with a 200 status code
        if user:
            return user.to_dict(), 200
        # If the session does not have a user_id, get() returns no data and a 401 (Unauthorized) status code
        else:
            return {}, 401


class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
