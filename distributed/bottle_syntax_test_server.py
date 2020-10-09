import bottle
#import requests
from bottle import route, run, template, post, get, request

class Rest_API:

    def __init__(self):
        pass

    def returns_string(self): #MIMICS GET REQUEST
        return "Hello World!"

    def returns_dynamic_string(self): #MIMICS POST REQUEST
        self.name = request.forms.get("name")
        return "Hello World! {}".format(self.name)

my_api = Rest_API()

bottle.route("/hello")(my_api.returns_string) #ASSOCIATES PATH WITH FUNCTION
bottle.route("/hello_dynamic", method = "POST")(my_api.returns_dynamic_string) #ASSOCIATES PATH WITH FUNCTION
run(host='localhost', port=8080, debug=True) #CREATES LISTENING SERVER
