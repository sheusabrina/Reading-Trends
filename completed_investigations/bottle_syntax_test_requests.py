import requests

#get_response = requests.get("http://localhost:8080/hello")
#get_content = get_response.content
#post_response = requests.post("http://localhost:8080/hello_dynamic", data = {"name": "Leora"})
#post_content = post_response.content
#print(post_content)

list_response = requests.get("http://localhost:8080/hello_list")
list_content = list_response.content
list_content = list_content.decode()
list_content = list_content.split(",")

chars_list = [",", "[", "]", " "]

new_list = []

for item in list_content:
    for char in chars_list:
        item = item.replace(char,"")
    item = int(item)
    new_list.append(item)

list_content = new_list

print(list_content)
print(type(list_content))
