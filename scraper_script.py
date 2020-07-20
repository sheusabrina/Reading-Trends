import requests


class Scraper():

    def __init__(self):
        pass

    def url_to_string(self, url):
        webpage_response = requests.get(url)
        webpage = webpage_response.content
        webpage_string = str(webpage)
        return webpage_string

    def string_to_file(self, file_name, string):
        open(file_name+".html", "w").write(string)

    def sleep(self, max_sleeptime):
        time_list = range(0, max_sleeptime, 0.1)
        sleeptime = random.choices(time_list)
        time.sleep(sleeptime)
