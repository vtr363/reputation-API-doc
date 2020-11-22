from bson.objectid import ObjectId

def evaluationJson(query):
	json = {"Evaluations":[],"Mean":0}
	med = 0
	count = 0
	for i in query:
		d = {}
		for j in i:
			if isinstance(i[j],ObjectId):
				d[j] =str(i[j])
			else:
				d[j] = i[j]
		json["Evaluations"].append(d)
		med += i["evaluation"]
		count +=1
	med = med/count
	json["Mean"] = med

	return json


def validateJson(json,keys,values_types):
	if not json:
		return "Bad Request: null json object",400
	else:
		for i in keys:
			if i not in json.keys():
				return "Bad Request: missing key '"+i+"', the keys to this request are "+str(keys), 400

		count = 0
		for i in json.keys():
			if i not in keys:
				return "Bad Request: invalid key, '"+str(i)+"' not in "+str(keys),400
			else:
				if type(json[i]) != values_types[count]:
					string = str(type(json[i])).split("'")[1]
					string2 = str(values_types[count]).split("'")[1]
					
					return "Bad Request: invalid value {}, from type {}, should be {}".format(str(json[i]),string,string2),400
	
				if type(json[i]) == list:
					count2 = 0
					for j in json[i]:
						if type(j) != str:
							string = str(type(j)).split("'")[1]
							string2 = str(str).split("'")[1]
							return "Bad Request: invalid value {} in {}, on position {}, from type {}, should be {}".format(str(j),
																													 str(keys[count]),
																													 str(count2),
																													 string,
																													 string2),400
						count2+=1
			count+=1
	return "Sucess!",201