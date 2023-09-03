from functions import * 
import socket
import threading

static_routes = []

class Color:  # Colors for print function
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

class http_server():
    def __init__(self, HOST="127.0.0.1", PORT=80, static_folder="static", log_user_data=False, session=False):
        self.routes = {}
        self.HOST = HOST
        self.PORT = PORT
        self.log_user_data = log_user_data
        self.static_folder = static_folder
        self.session = session

    # Return status code template data and file type
    def render_template(file_path, content_type = "text/html", custom_headers="" ):
        status_code, template_data = read_file(file_path)

        # # Create routes for css, js and images
        html_parser = BeautifulSoup(template_data, "html.parser")
        tag_list = [html_parser.find_all("link"), html_parser.find_all("script"), html_parser.find_all("img")]
        for tags in tag_list:
            for tag in tags:
                static_routes.append(tag.get("src"))  # Route, function to retrieve data
        return (template_data, status_code, content_type, custom_headers)

    def route(self, route):   # Decorator function
        def process_routes(func): # wrapper function
            self.routes[route] = func  # Store the routes for future use
        return process_routes  # run wrapper function

    def start(self):
        addr_list = [] 
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.bind((self.HOST, self.PORT))
        conn.listen()
        while True:
            try:
                print(f"Waiting for incoming connections at http://{self.HOST}:{self.PORT}")
                conn_socket, addr = conn.accept()
                for addrs in addr_list:
                    if addrs == addr:
                        conn.close() 
                addr_list.append(addr)
                print(addr)
                # connection_hander(conn_socket, web_pages)
                # thread conntion handler  
                threading.Thread(target=connection_handler, args=(
                                conn_socket, 
                                self.routes,
                                self.session,
                                static_routes,
                                self.HOST,
                                self.PORT,
                                self.log_user_data)
                                ).start()   
            except KeyboardInterrupt:
                print("Server Closing.")
                conn.close()
                quit()
    
    def register_blueprints(self, *blueprints):
        for blueprint in blueprints:
            for route, func in blueprint.routes.items():
                self.routes[route] = func

class connection_handler():
    def __init__(self, conn_socket, routes, session, static_routes, HOST="127.0.0.1", PORT=5000, log_user_data=False):
        self.conn_socket = conn_socket
        self.routes = routes  # store routes
        self.HOST = HOST 
        self.PORT = PORT 
        self.session = session
        self.log_user_data = log_user_data
        
        #### Run the receive_http and send_http  ###
        print("Client: ", self.conn_socket)
        print("Routes: ", self.routes)

        self.receive_http()
        

    def receive_http(self):
        # Receive requests
        request = self.conn_socket.recv(2048).decode()
        # Parse the requests 
        request_details = parser(request)
        print(request_details)

        # Send response
        self.send_http(request_details=request_details)


        # self.send_http(data="404 NOT FOUND", Content_Type="text/plain")
        # print(f"{Color.RED}404 NOT FOUND{Color.RESET}")

    # SEND HTTP RESPONSE
    def send_http(self, request_details):  # response   
        # for route, function in self.routes.items():
        #     if request_details[1] == route:
        #         output = function()
        print("\n\n Routes:", self.routes)
        custom_headers = ""
        output = ""
        content_type = "text/plain"
        # try:
        if self.routes.get(request_details[1]):
            output = self.routes[request_details[1]]()  # output is either tuple or response data
        
        elif request_details[1] in static_routes:
            output = static_file(static_routes.get(request_details[1]))   # output is either tuple or response data
            
        if ("tuple" in str(type(output))):
            data = output[0]
            status = output[1]
            content_type = output[2]
            custom_headers = output[3]   # Custom headers should be a dictionary
        elif output != "":
            data = output
            status = 200
        else:
            data = "404 File Not Found"
            status = 404
            
        # except:
        #     data = f"500 internal server error \n\n {request_details}"
        #     status = "500"
        #     content_type = "text/plain"
        
        response_parameters = {
            "Type": "Response",
            "Status_code": status,
            "Host": self.HOST,
            "Content_Type": content_type,
            "Content": data,
            # "X-Custom-Header": "Custom Value",
        }

        merge(custom_headers, response_parameters)  # Updates the response_parameters with custom_headers
        
        response = make_request(**response_parameters)
        
        self.conn_socket.send(response.encode())

        
    def log_data(self):
        ...


# app = http_server()

# @app.route("/")
# def home_page():
#     return "Welcome to the homepage"

# a = app.return_routes()
# print(a)

# result = a["/"]()
# print(result)