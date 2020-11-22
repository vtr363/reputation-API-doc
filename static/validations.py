import pymongo
from bson.objectid import ObjectId
import time

mb_user = "victor"
pwd = "dacDxB0jv8uEvRxc"


invalid_colaborator = ("Invalid Colaborator ID, please check if Colaborator ID value is correct",401)
invalid_colaborator_at_position = "Invalid Colaborator ID at position: "
invalid_user_at_position = "Invalid User ID at position: "
invalid_key = ("Invalid Aplication Key. Please check if Aplication Key value is correct",401)
deactivated_key = ("Your API access must be enabled. Please contact Support.",401)
passed_limit_key = ("You passed your limit of requisitions. Please contact Support to get another key",401)
invalid_question = ("Invalid Question Type {} at position: {}",401)
invalid_user = ("Invalid User ID, please check if User ID value is correct",401)
invalid_app = ("Invalid APP ID, please check if APP ID value is correct",401)

def validateEvaluation(key,uid,eid,questions,db):	
	application, flag = validateKey(key,db)
	if flag != 201:
		return application, flag

	application,flag = validateApplication(application["_id"],questions,db)
	if flag != 201:
		return application, flag

	user, flag = validateUser(uid,db)
	if flag != 201:
		return user, flag


	colaborator, flag = validateColaborator(eid,db)
	if flag != 201:
		return colaborator, flag

	return application, flag


def validateKey(key,db):
	#try:
	_application = db["Applications"].find_one({"key":key})

	if(not _application):
		return invalid_key

	elif not _application["key_status"]:
		return deactivated_key
	
	#elif _application["requisitions"] >= _application["limit"]:
	#	return passed_limit_key

	return _application, 201
	#except:
	#	return invalid_key	

def validateColaborator(cid,db):
	try:
		colaborator = db["Colaborators"].find_one({"_id":ObjectId(cid)},{"user_psw":0})

		if(not colaborator):
			return invalid_colaborator

		return colaborator, 201

	except:
		return invalid_colaborator	

def validateColaboratorList(cid_list,db,app_id):
	d = {}
	for i in range(len(cid_list)):
		try:
			colaborator = db["Colaborators"].find_one({"_id":ObjectId(cid_list[i])},{"user_psw":0})
			if(not colaborator):
				return invalid_colaborator_at_position+str(i),401
			else:
				d[cid_list[i]]=colaborator
				new_query = db["Avaliacoes"].find({"colaborator_id":ObjectId(cid_list[i]),"app_id":ObjectId(app_id)})
				
				if new_query:
					d[cid_list[i]]["evaluation"] = []
					count=0
					for j in new_query:
						d[cid_list[i]]["evaluation"].append({"Avaliação":j["evaluation"],
												 "Horário":time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(j["evaluation_time"])),
												 "Comentário":j["comment"]})

						if len(j["questions"]) > 0:
							for k in j["questions"]:
								d[cid_list[i]]["evaluation"][count][k] = j["questions"][k] 
						count+=1
				else:
					d[cid_list[i]]["evaluation"] = None
				
		except:
			return invalid_colaborator_at_position+str(i),401

	return d, 201

def validateUser(uid,db):
	try:
		user = db["Users"].find_one({"_id":ObjectId(uid)})
		if(not user):
			return invalid_user
	except:
		return invalid_user

	return user, 201

def validateApplication(aid,questions,db):
	try:
		app = db["Applications"].find_one({"_id":ObjectId(aid)})
		if(not app):
			return invalid_app

		if questions:
			for i in range(len(questions)):
				if type(questions[i]) != str:
					return invalid_question[0].format(type(questions[i]),i),invalid_question[1]

	except:
		return invalid_app

	return app, 201
