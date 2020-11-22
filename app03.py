import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, fields
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from bson.objectid import ObjectId
import static.forms as forms
import static.validations as val
import static.json as json_handler
import pymongo
import time
import os

mb_user = "victor"
pwd = "dacDxB0jv8uEvRxc"

app = Flask(__name__)
api = Api(app)
bootstrap = Bootstrap(app)
app.config["SECRET_KEY"] = "STRINGHARDTOGUESS"

client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@cluster0.d1wep.gcp.mongodb.net/RecDB?retryWrites=true&w=majority")
db = client.RecDB

#models
makeEvaluation = api.model('makeEvaluation',{"user_id":fields.String("5fb99c9970765b0beebd6a25"),
										   "colaborator_id":fields.String('5fb99c9a70765b0beebd6a26'),
										   "key":fields.String('genericKey'),
										   "evaluation":fields.Float(),
										   "comments":fields.String(),
										   "questions":fields.List(fields.String('O que achou?'))})

evaluationByApp = api.model('evaluationByApp',{"app_id": fields.String('5fb99c9a70765b0beebd6a27'),
												"colaborator_id":fields.String('5fb99c9a70765b0beebd6a26')})

fullEvaluation = api.model('fullEvaluation',{"colaborator_id":fields.String('5fb99c9a70765b0beebd6a26')})

ManageColaborators = api.model('ManageColaborators', {"key":fields.String('genericKey'),
													"colaborator_list":fields.List(fields.String('5fb99c9a70765b0beebd6a26')),
													"status_list":fields.List(fields.String('True'))})



@api.route('/makeEvaluation', doc = {"description": 'Create or update an Evaluation',
									"params": {"user_id": "the id of the user that is Evaluating \n Ex: 5fb99c9970765b0beebd6a25 ",
												"colaborator_id": "the id of the colaborator who is being Evaluated \n Ex: 5fb99c9a70765b0beebd6a26",
												"key": "the key of the application \n Ex: genericKey",
												"evaluation": "the score given by the user",
												"comments": "the comments of the user",
												"questions": "the questions of the aplication"}})
class makeEvaluation(Resource):

	@api.expect(makeEvaluation)
	def post(self):	
		if request.content_type != "application/json":
			return "Bad Request. Content Type must be application/json", 400

		data = api.payload
		keys = ["user_id","colaborator_id","key","evaluation","comments","questions"]
		value_types = [str,str,str,float,str,list]

		#Validates JSON
		msg,flag = json_handler.validateJson(dict(data),keys,value_types)
		if flag != 201:
			return msg,flag

		#Validates Colaborator
		_application, flag = val.validateEvaluation(data["key"],
			                                        data["user_id"],
			                                        data["colaborator_id"],
			                                        data["questions"],
			                                        db)
		if flag != 201:
			return _application, flag

		if len(data["questions"]) < len(_application["questions"]):
			size1 = len(data["questions"])
			size2 = len(_application["questions"])
			return "Size of 'questions' list is {}, it should be {}".format(size1,size2),400

		_questions = {}
		count = 0
		for i in _application["questions"]:
			_questions[i]=data["questions"][count]
			count+=1

		query = db["Avaliacoes"].find_one({"app_id":ObjectId(_application["_id"]),
									   "user_id":ObjectId(data["user_id"]),
									   "colaborator_id":ObjectId(data["colaborator_id"])})
		if(query):
			db["Avaliacoes"].update_one(query,{"$set":{"evaluation":data["evaluation"],
													   "evaluation_time":time.time(),
													   "comments":data["comments"], 
													   "questions":_questions}})
			return "Evaluation updated succesfully",201
		else:
			
			_id = db["Avaliacoes"].insert_one({"app_id":ObjectId(_application["_id"]),
											   "user_id":ObjectId(data["user_id"]),
											   "colaborator_id":ObjectId(data['colaborator_id']),
											   "evaluation":data["evaluation"],
											   "evaluation_time":time.time(),
											   "comment":data["comments"],
											   "questions":_questions})
			return "Evaluation created succesfully",201

@api.route('/evaluationByApp', doc = {"description": "Gets all the evaluations of a colaborator in a specific application",
									"params": {"app_id": "The id of the application",
												"colaborator_id": "The id of the colaborator"}})
class evaluationByApp(Resource):
	@api.expect(evaluationByApp)	
	# no caso esse deveria ser GET//
	def post(self):
		#Verifies the content of the request
		if request.content_type != "application/json":
			return "Bad Request. Content Type must be application/json", 400

		#Gets request JSON
		data = api.payload
		keys = ["app_id","colaborator_id"]
		value_types = [str,str]

		#Validates JSON
		msg,flag = json_handler.validateJson(dict(data),keys,value_types)
		if flag != 201:
			return msg,flag

		#Validates Colaborator
		msg, flag = val.validateColaborator(data["colaborator_id"],db)
		if flag!=201:
			return msg, flag

		#Gets all evaluations to a specific APP
		query = db["Avaliacoes"].find({"app_id":ObjectId(data["app_id"]),"colaborator_id":ObjectId(data["colaborator_id"])},{"_id":0,"app_id":0,"colaborator_id":0,"user_id":0,"key":0})
		
		if(query):
			json = json_handler.evaluationJson(query)
			return json,200
		else:
			return None,200

@api.route('/fullEvaluation', doc = {"description": "Gets all evaluations made on an specific colaborator",
									"params": {"colaborator_id": "the id of the colaborator"}})
class fullEvaluation(Resource):

	@api.expect(fullEvaluation)
	def post(self):
		#Verifies the content of the request
		if request.content_type != "application/json":
			return "Bad Request. Content Type must be application/json", 400

		#Gets the request JSON
		data = api.payload
		keys = ["colaborator_id"]
		value_types = [str]

		#Validates the request JSON
		msg,flag = json_handler.validateJson(dict(data),keys,value_types)
		if flag != 201:
			return msg,flag

		#Validates Colaborator
		_colaborator, flag = val.validateColaborator(data["colaborator_id"],db)
		if flag!=201:
			return _colaborator, flag

		#Gets all evaluations made on this colaborator
		query = db["Avaliacoes"].find({"colaborator_id":ObjectId(data["colaborator_id"])},{"_id":0,"key":0})

		if(query):
			json = json_handler.evaluationJson(query)
			return json, 200
		else:
			return None, 200

@api.route("/ManageColaborators/GET_METHOD", doc = {"description": "updates the Colaborators depending on the method given \nThis route is the same as '/ManageColaborators' but require a GET method",
													"params": {"key": "the key of the application",
																"colaborator_list": "A list of the colaboratos that you want to manage",
																"status_list": "a list of the status of the colaborators that are being managed"}})
class ManageColaborators_GET_METHOD(Resource):
	@api.expect(ManageColaborators)
	def post(self):
		#Verifies the content of the request
		if request.content_type != "application/json":
			return "Bad Request. Content Type must be application/json", 400

		#Gets the request JSON
		data = api.payload
		keys = ["key","colaborator_list","status_list"]
		value_types = [str,list,list]
		
		#Validates the request JSON
		msg,flag = json_handler.validateJson(dict(data),keys,value_types)
		if flag != 201:
			return msg,flag	

		#Validates Key
		_application, flag = val.validateKey(data["key"],db)
		if flag != 201:
			return _application, flag

		#Validates Colaborators
		colaborators, flag = val.validateColaboratorList(data["colaborator_list"],db,str(_application["_id"]))
		if flag != 201:
			return colaborators, flag

		#Separates by method(GET)
		d = {}
		for i in colaborators.keys():
			d[i]={}
			for j in colaborators[i]:
				if j != "_id":
					d[i][j]=colaborators[i][j]
		return d, 226

@api.route("/ManageColaborators",methods=["GET","POST","DELETE"], doc = {"description": "updates the Colaborators depending on the method given",
																		"params": {"key": "the key of the application",
																					"colaborator_list": "A list of the colaboratos that you want to manage",
																					"status_list": "a list of the status of the colaborators that are being managed"}})
class ManageColaborators(Resource):

	@api.expect(ManageColaborators)
	def post(self):
		#Verifies the content of the request
		if request.content_type != "application/json":
			return "Bad Request. Content Type must be application/json", 400

		#Gets the request JSON
		data = api.payload
		keys = ["key","colaborator_list","status_list"]
		value_types = [str,list,list]
		
		#Validates the request JSON
		msg,flag = json_handler.validateJson(dict(data),keys,value_types)
		if flag != 201:
			return msg,flag	

		#Validates Key
		_application, flag = val.validateKey(data["key"],db)
		if flag != 201:
			return _application, flag

		#Validates Colaborators
		colaborators, flag = val.validateColaboratorList(data["colaborator_list"],db,str(_application["_id"]))
		if flag != 201:
			return colaborators, flag

		#Separates by method
		if request.method == "POST":
			if len(data["colaborator_list"]) != len(data["status_list"]):
				return "Bad Request: lenghts of colaborator_list and status_list must match",400
			#Updates the Database
			d={}
			for i in range(len(data["colaborator_list"])):
				d["colaborators."+data["colaborator_list"][i]] = data["status_list"][i]
			db["Applications"].update_one(_application,{"$set":d})
			return "Colaborators updated succesfully", 201

		elif request.method == "DELETE":
			#Updates the Database
			d={}
			for i in range(len(data["colaborator_list"])):
				d["colaborators."+data["colaborator_list"][i]] = ""
			db["Applications"].update_one(_application,{"$unset":d})

			return "",204

		elif request.method == "GET":
			d = {}
			for i in colaborators.keys():
				d[i]={}
				for j in colaborators[i]:
					if j != "_id":
						d[i][j]=colaborators[i][j]
			return d, 226

	

	@api.expect(ManageColaborators)
	def delete(self):
		#Verifies the content of the request
		if request.content_type != "application/json":
			return "Bad Request. Content Type must be application/json", 400

		#Gets the request JSON
		data = api.payload
		keys = ["key","colaborator_list","status_list"]
		value_types = [str,list,list]
		
		#Validates the request JSON
		msg,flag = json_handler.validateJson(dict(data),keys,value_types)
		if flag != 201:
			return msg,flag	

		#Validates Key
		_application, flag = val.validateKey(data["key"],db)
		if flag != 201:
			return _application, flag

		#Validates Colaborators
		colaborators, flag = val.validateColaboratorList(data["colaborator_list"],db,str(_application["_id"]))
		if flag != 201:
			return colaborators, flag

		#Separates by method
		if request.method == "POST":
			if len(data["colaborator_list"]) != len(data["status_list"]):
				return "Bad Request: lenghts of colaborator_list and status_list must match",400
			#Updates the Database
			d={}
			for i in range(len(data["colaborator_list"])):
				d["colaborators."+data["colaborator_list"][i]] = data["status_list"][i]
			db["Applications"].update_one(_application,{"$set":d})
			return "Colaborators updated succesfully", 201

		elif request.method == "DELETE":
			#Updates the Database
			d={}
			for i in range(len(data["colaborator_list"])):
				d["colaborators."+data["colaborator_list"][i]] = ""
			db["Applications"].update_one(_application,{"$unset":d})

			return "",204

		elif request.method == "GET":
			d = {}
			for i in colaborators.keys():
				d[i]={}
				for j in colaborators[i]:
					if j != "_id":
						d[i][j]=colaborators[i][j]
			return d, 226


if __name__ == '__main__':
	app.run(debug=True)
