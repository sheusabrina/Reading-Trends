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

    def generic_function(self, input):
        return "Generic Function Result: {}".format(input)

my_api = Rest_API()

bottle.post("/generic_url")(my_api.generic_function("request text"))

run(host='localhost', port=8080, debug=True)
