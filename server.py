#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask

# Modifications to the code licensed under CC BY-SA 4.0 by Danila Seliayeu, 
 #2021 https://creativecommons.org/licenses/by-sa/4.0/



import re
import flask
from flask import Flask, request, redirect, jsonify
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry
        self.notify_all(entity, self.space[entity])

    def set(self, entity, data):
        self.space[entity] = data
        self.notify_all(entity, data)

    def clear(self):
        self.space = dict()
        self.listeners = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

# code below referenced from https://github.com/uofa-cmput404/cmput404-slides/tree/master/examples/ObserverExampleAJAX
# which is written by Hazel Campbell

    def add_listener(self, listener):
        self.listeners[listener] = dict()
    
    def get_listener(self, listener):
        return self.listeners[listener]
    
    def clear_listener(self, listener):
        self.listeners[listener] = dict()

    def notify_all(self, entity, data):
        for listener in self.listeners:
            self.listeners[listener][entity] = data

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    return redirect("/static/index.html")

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    if request.method == "PUT":
        res = request.json
        if not res: res = flask_post_json()
        myWorld.set(entity, res)
        return jsonify(myWorld.get(entity));
    elif request.method == "POST":
        res = request.json
        if not res: res = flask_post_json()
        for key in res:
            myWorld.update(entity, key, res[key])
        return jsonify(myWorld.world());
    # add error stuff 
    return None

@app.route("/world", methods=['POST','GET'])    
def world():
    return jsonify(myWorld.world());

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, returns a representation of the entity'''
    return jsonify(myWorld.get(entity));

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear();
    return jsonify(myWorld.world());

# listener-related code below taken from https://github.com/uofa-cmput404/cmput404-slides/tree/master/examples/ObserverExampleAJAX
# which is written by Hazel Campbell
@app.route("/listener/<entity>", methods=['POST','PUT'])
def add_listener(entity):
    myWorld.add_listener( entity )
    return jsonify(dict())

@app.route("/listener/<entity>")    
def get_listener(entity):
    v = myWorld.get_listener(entity)
    myWorld.clear_listener(entity)
    return jsonify( v )



if __name__ == "__main__":
    app.run()
