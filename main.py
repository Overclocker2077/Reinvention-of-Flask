import http_server2 as http

HOST = "127.0.0.1"
PORT = 5000

app = http.http_server(HOST=HOST, PORT=PORT, static_folder="templates")

@app.route("/")
def home_page():
    return app.render_template(file_path="templates/index.html")

@app.route("/hello")
def hello_page():
    return "Hello"

if __name__ == "__main__":
    app.start()

