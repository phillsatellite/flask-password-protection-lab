#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

api.add_resource(ClearSession, '/clear', endpoint='clear')

class Signup(Resource):
    
    def post(self):
        data = request.get_json()
        
        #Create new user
        new_user = User(username = data['username'])
        new_user.password_hash = data['password']
        
        #Save to db
        db.session.add(new_user)
        db.session.commit()

        #Log user in with session
        session['user_id'] = new_user.id

        #Return user object as json
        schema = UserSchema()
        return schema.dump(new_user), 201
    
api.add_resource(Signup, '/signup', endpoint='signup')

class CheckSession(Resource):

    def get(self):
        #Lookup the user by their session ID
        user_id = session.get('user_id')

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            schema = UserSchema()
            return schema.dump(user), 200
        else:
            return {}, 204

api.add_resource(CheckSession, '/check_session', endpoint='check_session')

class Login(Resource):

    def post(self):
        data = request.get_json()

        #Find the user by username
        user = User.query.filter_by(username=data['username']).first()

        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            schema = UserSchema()
            return schema.dump(user), 200
        
        return {'error': 'Invalid username or password'}, 401

api.add_resource(Login, '/login', endpoint='login')

class Logout(Resource):

    def delete(self):
        
        #Remove user from session
        session['user_id'] = None
        return {}, 204

api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
