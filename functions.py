import json
from bs4 import BeautifulSoup

encode_dict = {
    r" ": "+",
    r"!": r"%21",
    r'"': r"%21",
    r"#": r"%25",
    r"$": r"%24+",
    r"%": r"%25",
    r"&": r"%26",
    r"'": r"%27",
    r"(": r"%28",
    r")": r"%29",
    r"+": r"%2B",
    r",": r"%2C",
    r"/": r"%2F",
    r":": r"%3A",
    r";": r"%3B",
    r"<": r"%3C",
    r"=": r"%3D",
    r">": r"%3E",
    r"?": r"%3F",
    r"@": r"%40",
    r"[": r"%5B",
    r"\\": r"%5C",
    r"]": r"%5D",
    r"^": r"%5E",
    r"`": r"%60",
    r"{": r"%7B",
    r"|": r"%7C",
    r"}": r"%7D",
    r"~": r"%7E"
}

# class Error(Exception): print("Error")

def decode_url(data):
    data = list(data)
    for key, value in encode_dict.items():
        for i in range(len(data)):
            if data[i:i+len(value)] == list(encode_dict[key]):
                data[i:i+len(value)] = key 
    return "".join(data)

def encode_url(data):
    data = list(data)
    for key, value in encode_dict.items():
        for i in range(len(data)):
            if data[i] == key:
                data[i] = value
    return "".join(data)

def parser(requests):    # The parser will convert the HTTP requests into a python dictionary
    if requests != "":
        req_dict = {}
        split_line = requests.replace("\r", "").split("\n")
        # This part parsers the status line 
        status_line = split_line[0]
        # print(split_line[0])
        status_line_list = status_line.split(" ")
        # HTTP Method 
        # print(f"Status_line:  {status_line_list}")
        request_method = status_line_list[0]
        endPoint_PATH = status_line_list[1]
        protocol_version = status_line_list[2]

        for i in range(len(split_line)):
            if i != 0 and ":" in split_line[i]:
                split = split_line[i].split(":")
                req_dict[split[0]] = split[1]
        data = split_line[len(split_line)-1]

        return [request_method, endPoint_PATH, protocol_version, req_dict, data]  # return list(requests_type, requests_file, protocol_version,  dict{requests_headers}, data)
    return None

def formData_parser(requests):
    form_data = {}
    requests_lines = requests.split("\n")
    form_data_split1 = requests_lines[len(requests_lines)-1].split("&")
    form_data_split2 = [data.split("=") for data in form_data_split1]
    for i in range(len(form_data_split2)):
        form_data[form_data_split2[i][0]] = decode_url(form_data_split2[i][1])
    return form_data

def json_parser(requests):  # JSON parser for requests 
    start_line = None
    form_data = {}
    requests_lines = requests.split("\n")
    for i in range(len(requests_lines)):  # starting line for the json data
        if requests_lines[i] == "": 
            start_line = i 
            break
    return json.loads("".join(requests_lines[start_line:]))

content_types_dict = {
                      "html": "text/html", 
                      "css": "text/css", 
                      "mp4": "video/mp4", 
                      "png": "image/png", 
                      "js": "application/javascript", 
                      "json": "application/json",
                      "jpg": "image/jpeg",
                      "jpeg": "image/jpeg"
                      }

def file_type(file_name):  # returns Content-Types for file
    file_extension = file_name.split(".")[1]
    for key, value in content_types_dict.items():
        if key == file_extension:
            return value
    
    print("Unsupported file type")
    return "text/plain"

# wip
def process_json(json_data):
    data_dict = [json.loads(json_data) if "str" in str(type(json_data)) else json_data][0]
    process_json_string = []
    for key, value in data_dict.items():
        if key != "" and value != "":
            process_json_string.append(f"{key}: {value}\r\n")
    processed_json_string ="".join(process_json_string)
    return processed_json_string

def make_request(**kwargs):  
    """ GET & POST only \n
    kwargs for making a custom http requests or response\n
    Type: response or request\n
    Route: use for request only\n
    Status_code\n
    Host\n
    Content_Type\n
    Content_Length\n
    Connection: keep-alive\n
    Content\n
    Method: POST or GET\n
    Some http headers are automatically set but can be set manually as parameters\n
    You can add custom http headers headers if needed \n
    """

    version = "HTTP/2"
    # r = ""
    # host = kwargs.get("Host")
    # content_type = kwargs.get("Content_Type")
    content = ["" if kwargs.get("Content") == None else kwargs.get("Content")][0]
    if not ("bytes" in str(type(content))) and content != None:
        content = content.encode()
    r_type = kwargs.get("Type") # http type 
    connection = ["keep-alive" if kwargs.get("Connection") == None else kwargs.get("Connection")][0]
    method = kwargs.get("Method")
    status_code = kwargs.get("Status_code")
     # kwargs to skip for custom headers
    default_kwargs = ["Route", "Host", "Content_Length", "Content_Type",  "Content", "Type", "Connection", "Method", "Status_code"]
    route = kwargs.get('Route')
    # Prepare headers
    headers = {  
        "Host": kwargs.get("Host"),
        "Content-Type" if r_type == "Response" else "" : kwargs.get("Content_Type") if r_type == "Response" else "" ,
        "Content-Length": len(content) if r_type == "Response" and content!=None else 0,
    }  
    # Prepare custom headers
    for key, value in kwargs.items():
        if not (key in default_kwargs):
            headers[key] = value

    # Add status line with headers
    if r_type == "Response":
        status_line = f"{version} {status_code}"
        if status_code == 200: status_line = status_line+" OK"
    if r_type == "Request": status_line = f"{method} {route} {version}"
    if content == None: content=b""
    return status_line.encode()+b"\n"+process_json(headers).encode()+b"\n"+content

def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return "200", file.read()
    except FileNotFoundError:
        return "404 FILE NOT FOUND"

def merge(dict1, dict2):
    return(dict2.update(dict1))

def readb(file_path):
    try:
        with open(file_path, "rb") as file:
            return "200", file.read()
    except:  
        return ("FILE NOT FOUND", "404")
    
static_routes = []

# Return status code template bytes data and file type
def render_template(file_path, content_type = "text/html"):
    status_code, template_data = read_file(file_path)

    # # Create routes for css, js and images
    html_parser = BeautifulSoup(template_data, 'html.parser')
    tag_list = [html_parser.find_all("link"), html_parser.find_all("script"), html_parser.find_all("img")]
    for tags in tag_list:
        for tag in tags:
            static_routes.append(tag.get("src"))  # Route, function to retrieve data
            

    return template_data, status_code, content_type

# render_template("templates/index.html")

# Return Status code static bytes data and file type
def static_file(file_name, static_folder):
    try:
        with open(f"{static_folder}/{file_name}", "rb") as file:
            return (file.read(), 200, file_type(file_name), "")  # Data, status_code, content_type
    except FileNotFoundError:
        return (f"404 File Not Found {static_folder}/{file_name}", 404, "text/plain", "")


# Blueprint for import routes to other files  
class Blueprints():
    def __init__(self):
        self.routes = {}

    def route(self, route):   # Decorator function
        def process_routes(func): # wrapper function
            self.routes[route] = func  # Store the routes for future use
        return process_routes  # run wrapper function



# # Set parameters for the request
# request_params = {
#     "Type": "Request",
#     "Method": "GET",
#     "Host": "example.com",
#     "Route": "/api/resource",
# }

    # response_params = {  # Payload with
    # "Type": "Response",
    # "Status_code": "200",
    # "Host": "",
    # "Content_Type": "text/plain",
    # "Body": ,
    # "X-Custom-Header": "Custom Value",
    # }

# # data = {"Host": "example.com", "": "", "Content-Length": 0, "Route": "/api/resource"}
# # process_json(data)

# # Make the request
# response = make_request(**request_params)

# Print the response
# print(response)
# print("\n")
# Set parameters for the response
# response_params = {  # Payload with
#     "Type": "Response",
#     "Status_code": 200,
#     "Host": "example.com",
#     "Content_Type": "text/plain",
#     "Body": "You have been hack retard!",
#     "X-Custom-Header": "Custom Value",
# }

# # Make the response
# response = make_request(**response_params)

# # Print the response
# print(response)
# print("\n")

# response_dict = parser(response)

# print(response_dict)


# a = """POST /api/endpoint HTTP/1.1
# Host: example.com
# Content-Type: application/json
# Content-Length: 36

# {"name":"John","age":30}
# """

# b = parser(a)

# print(b)