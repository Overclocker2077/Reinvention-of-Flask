import http_server2 as http

HOST = "127.0.0.1"
PORT = 5000

app = http.http_server()

@app.route("/")
def home_page():
    return "welcome to my website"

if __name__ == "__main__":
    app.start(HOST, PORT)

