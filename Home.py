import flask
from flask import jsonify, request
from flaskext.mysql import MySQL
import logging

app = flask.Flask(__name__)
app.config["DEBUG"] = True
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mohan1111'
app.config['MYSQL_DATABASE_DB'] = 'medicalapplication'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


@app.route('/', methods=['GET'])
def home():
    logging.info('Home Page was clicked')
    return "<h1>Home Page</h1>"


@app.route('/register', methods=['POST'])
def register():
    user_name = str(request.form.get('user_name'))
    user_password = str(request.form.get('user_password'))
    user_mobile = str(request.form.get('user_mobile'))

    logging.info(user_name)
    logging.info(user_mobile)
    logging.info(user_password)
    conn = mysql.connect()
    logging.info('Connecting to DB')
    cursor = conn.cursor()
    logging.info('DB Connection Successful Executing Query')
    cursor.execute("select user_id from users where user_name=%s", user_name)
    data = cursor.fetchone()

    if data is not None:
        return jsonify({"errorMessage": "User_name already available"})
    else:
        cursor.execute("SELECT user_id from counter")
        user_id = cursor.fetchone()[0]
        logging.info(user_id)
        query = "INSERT INTO users(user_id,user_name,user_password,user_mobile,is_logged_in) VALUES (%s,%s,%s,%s,%s)"

        cursor.execute(query, (user_id, user_name, user_password, user_mobile, "False"))
        conn.commit()
        user_id += 1
        cursor.execute("UPDATE counter set user_id=%s", user_id)
        conn.commit()
    return jsonify({"successMessage": "User Added Successfully"})


@app.route('/login', methods=['POST'])
def login():
    user_name = str(request.form.get('user_name'))
    user_password = str(request.form.get('user_password'))
    conn = mysql.connect()
    logging.info('Connecting to DB')
    cursor = conn.cursor()
    logging.info("DB Connection Successful Executing Select Query")
    cursor.execute("SELECT user_password from users where user_name = %s", user_name)
    password_from_query = cursor.fetchone()
    if password_from_query is None:
        return jsonify({"errorMessage": "User Doesn't Exist"})
    if password_from_query[0] == user_password:
        cursor.execute("UPDATE users set is_logged_in=%s where user_name = %s", ('True', user_name))
        conn.commit()
        return jsonify({"successMessage": "User Logged In"})
    else:
        return jsonify({"errorMessage": "Invalid Password"})


@app.route('/logout', methods=['GET'])
def logout():
    if 'user_name' in request.args:
        user_name = request.args['user_name']
    else:
        return jsonify({"errorMessage": "Required Parameter Missing"})
    conn = mysql.connect()
    logging.info('Connecting to DB')
    cursor = conn.cursor()
    logging.info("DB Connection Successful Executing Query")
    cursor.execute("SELECT user_id from users where user_name = %s", user_name)
    data = cursor.fetchone()
    if data is None:
        return jsonify({"errorMessage": "User Doesn't Exist"})
    else:
        cursor.execute("UPDATE users set is_logged_in=%s where user_name = %s", ('False', user_name))
        conn.commit()
        return jsonify({"successMessage": "User Logged Out"})


app.run()
