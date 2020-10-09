from bottle import route, run, template, post, get

#BOTTLE QUICKSTART 

@route('/hello')
def hello():
    return "Hello World!"

run(host='localhost', port=8080, debug=True)

#TEST visit http://localhost:8080/hello
