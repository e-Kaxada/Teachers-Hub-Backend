from database_handler import DbConn
from flask import jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from src.validators.user_validator import ValidateUser


class UserController:

    """User controller interfaces with the database."""

    def __init__(self):
        """Initializes the user controller class."""
        conn = DbConn()
        self.cur = conn.create_connection()
        conn.create_users_table()

    def create_user(self, data):
        """Creates a user.
        Arguments:
          data {[email, username, password, firstname, lastname, role ]} --
          [Signup details needed]
        """
        sql = """INSERT INTO users(email, username, password, firstname,
                                    lastname, role)
                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}')"""

        hashed_password = generate_password_hash(data['password'], 'sha256')

        sql_command = sql.format(data['email'],
                                 data['username'],
                                 hashed_password,
                                 data['firstname'],
                                 data['lastname'],
                                 data['role'])
        self.cur.execute(sql_command)

    def register_user_controller(self, data):
        validate = ValidateUser(data)
        is_valid = validate.is_valid()

        if is_valid == "valid":
            if not self.check_duplicate_email(data['email']):
                if not self.check_duplicate_username(data['username']):
                    self.create_user(data)
                    return jsonify({"message":
                                    "user registered successfully"}), 201
                return jsonify({"message": "Username already exists"}), 400
            return jsonify({"message": "Email already exists"}), 400
        return jsonify({"message": is_valid}), 400

    def login_user(self, username, password):
        """Logs in a user

        Arguments:
          data {[username, password ]} -- [Login credentials needed]
        """
        sql = """SELECT username,password FROM users WHERE username='{}'"""
        self.cur.execute(sql.format(username))
        db_user = self.cur.fetchone()
        if not db_user:
            return jsonify({'message': 'No user found'}), 404
        if not check_password_hash(db_user[1], password):
            return jsonify({'message': 'Invalid password'}), 400
        else:
            access_token = create_access_token(identity=username)
            return jsonify({'message': 'successfully logged in',
                            'token': access_token
                            }), 200

    def check_duplicate_email(self, the_email):
        '''
            checks the email submitted by user
            during registration to see if it already exists
        '''

        sql_email = """SELECT email FROM users WHERE email='{}'"""
        self.cur.execute(sql_email.format(the_email))
        db_email = self.cur.fetchone()
        if db_email:
            return True
        else:
            return False

    def check_duplicate_username(self, the_username):
        '''
            checks the email submitted by user
            during registration to see if it already exists
        '''

        sql_username = """SELECT username FROM users WHERE username='{}'"""
        self.cur.execute(sql_username.format(the_username))
        db_username = self.cur.fetchone()
        if db_username:
            return True
        else:
            return False
