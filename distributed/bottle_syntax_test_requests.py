import requests

get_response = requests.get("http://localhost:8080/hello")
get_content = get_response.content
print(get_content)

post_response = requests.post("http://localhost:8080/hello_dynamic", data = "Leora")
post_content = post_response.content
print(post_content)
