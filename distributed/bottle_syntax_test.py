import bottle
from bottle import route, run, template, post, get

#BOTTLE QUICKSTART

#@route('/hello')
#def hello():
    #return "Hello World!"

#run(host='localhost', port=8080, debug=True)

#VALIDATION visit http://localhost:8080/hello

class Rest_API:

    def __init__(self):
        pass

    def generic_function(self):
        return("Generic Function Result")

my_api = Rest_API()

bottle.route("/generic_url")(my_api.generic_function)

run(host='localhost', port=8080, debug=True)
