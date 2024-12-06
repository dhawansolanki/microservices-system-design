import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

#config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "12345678")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "auth")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT", "3306")


@server.route("/login", methods=["POST"])
def login(request):
    auth = request.authorization
    if not auth:
        return "Missing username or password", 401
    
    # Check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT * FROM users WHERE email = %s",(auth.username)
    )
    if res > 0:
        user_row = res.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "Invalid username or password", 403
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET", ""), True)
    else:
        return "Invalid username.", 403
    
@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200
    
def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.datetime.utc) + datetime.timedelta(daya=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz
        },
        secret,
        algorithm="HS256"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)