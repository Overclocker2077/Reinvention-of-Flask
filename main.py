import http_server2 as http
# from http_server2 import http_server as http, requestD, 

HOST = "127.0.0.1"
PORT = 5000

app = http.http_server(HOST=HOST, PORT=PORT, static_folder="templates")

@app.route("/")
def home_page(**kwargs):
    return app.render_template(file_path="templates/index2.html")

@app.route("/hello")
def hello_page(**kwargs):
    return f"Hello {kwargs.get('request')}"

if __name__ == "__main__":
    app.start()

