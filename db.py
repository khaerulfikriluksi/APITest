import mysql.connector
from datetime import datetime, timedelta
import string
import random
from typing import List, Tuple
import pytz

class Database:
    __instance = None

    @staticmethod
    def get_instance():
        if Database.__instance is None:
            Database()
        return Database.__instance

    def __init__(self):
        if Database.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Database.__instance = self
            self.connection = mysql.connector.connect(
                host="153.92.15.3",
                user="u357102271_OTP",
                password="FikriLuksi321@@@",
                database="u357102271_OTP"
            )
            self.cursor = self.connection.cursor()
            print("Connected to MySQL")

    
    def insert_order(self, username, application, order_time):
        idNumber = self.generate_random_string()
        self.cursor.execute('''
            INSERT INTO tbl_order (id, username, application, order_time, `status`)
            VALUES (%s, %s, %s, %s, %s)
        ''', (idNumber, username, application, order_time, 'New'))

        self.connection.commit()
        
    #--------NewUpdate--------------------#
    
    def add_order(self, data, username):
        query = """
        INSERT INTO tbl_order (id, username, application, order_time, number, message, status, order_status, read_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['id'],
            username,
            data['application'],
            data['order_time'],
            data['number'],
            data['message'],
            data['status'],
            data['order_status'],
            "New"
        )
        self.cursor.execute(query, params)
        self.connection.commit()
    
    def update_order_timeout(self, order_id, message, status, order_status, readstatus):
        query = """
        UPDATE tbl_order
        SET message = %s, status = %s, order_status = %s, read_status = %s
        WHERE id = %s
        """
        self.cursor.execute(query, (message, status, order_status, readstatus, order_id))
        self.connection.commit()
    
    def update_order(self, order_id, message, status, readstatus):
        query = """
        UPDATE tbl_order
        SET message = %s, status = %s, read_status = %s
        WHERE id = %s
        """
        self.cursor.execute(query, (message, status, readstatus, order_id))
        self.connection.commit()
        
    def get_deleted_id(self, username):
        query = """
        SELECT id FROM tbl_order
        WHERE `status` = 'Waiting Sms' AND order_status = 'Ongoing' AND username = %s
        """
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]
        
    def get_sms_empty_id(self):
        query = """
        SELECT id FROM tbl_order
        WHERE `status` = 'Waiting Sms' AND order_status = 'Ongoing'
        """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return [row[0] for row in result]
    
    def get_application(self) -> List[Tuple[str, str]]:
        query = "SELECT application, cost FROM tbl_application"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_user_data(self, username: str) -> List[Tuple[str, str]]:
        query = "SELECT email, password FROM tbl_customer WHERE username = %s"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    #--------------------------------------------#
    
    def generate_random_string(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(5))

    def check_order_exists(self, number):
        self.cursor.execute("SELECT COUNT(*) FROM tbl_order WHERE number = %s", (number,))
        result = self.cursor.fetchone()[0]
        return result > 0

    def check_order_to_delete(self, username):
        # Mengambil waktu saat ini dan mengurangi 2 menit
        now_minus_2_minutes = datetime.now(pytz.timezone('Asia/Jakarta')) - timedelta(minutes=2)
        formatted_time = now_minus_2_minutes.strftime('%Y-%m-%d %H:%M:%S')

        # Menambahkan kondisi waktu ke dalam query SQL
        #self.cursor.execute("SELECT COUNT(*) FROM tbl_order WHERE `status` = 'Waiting Sms' AND order_status = 'Ongoing' AND username = '"+username+"' AND order_time < '"+formatted_time+"'")
        self.cursor.execute("SELECT COUNT(*) FROM tbl_order WHERE `status` = 'Waiting Sms' AND order_status = 'Ongoing' AND username = '"+username+"'")
        result = self.cursor.fetchone()[0]
        return result > 0
    
    def check_ongoing(self, username):
        # Menambahkan kondisi waktu ke dalam query SQL
        self.cursor.execute("SELECT COUNT(*) FROM tbl_order WHERE `status` = 'Waiting Sms' AND order_status = 'Ongoing' AND username = '"+username+"'")
        result = self.cursor.fetchone()[0]
        return result > 0
    
    def check_ongoing_not_send(self, username):
        # Menambahkan kondisi waktu ke dalam query SQL
        self.cursor.execute("SELECT COUNT(*) FROM tbl_order WHERE `status` = 'Success' AND order_status = 'Ongoing' AND username = '"+username+"' ")
        result = self.cursor.fetchone()[0]
        return result > 0

    def check_on_order(self, username):
        self.cursor.execute("SELECT COUNT(*) FROM tbl_order WHERE order_status = 'Ongoing' AND `status` like '%waiting%' AND username = %s LIMIT 1", (username,))
        result = self.cursor.fetchone()[0]
        return result > 0
    
    def get_number(self, username) -> List[Tuple[str, str]]:
        self.cursor.execute('SELECT `number`, `application` FROM tbl_order WHERE `username`="'+username+'" AND `order_status`="Ongoing" AND `status` like "%waiting%" LIMIT 1')
        return self.cursor.fetchall()

    def get_orders(self, username: str) -> List[Tuple[str, str, str, str, str]]:
        self.cursor.execute('''
            SELECT number, application, order_time, message, `status`
            FROM tbl_order
            WHERE username = %s AND order_status = %s
            LIMIT 1
        ''', (username, 'Ongoing'))
        return self.cursor.fetchall()
    
    
    
    def get_config(self) -> List[Tuple[str, str]]:
        self.cursor.execute('SELECT whatsapp_number, token FROM tbl_config LIMIT 1')
        return self.cursor.fetchall()

    def keep_alive(self) -> List[Tuple[str]]:
        self.cursor.execute('SELECT 1')
        return self.cursor.fetchall()

    def update_finish_order(self, username, number):
        self.cursor.execute('UPDATE tbl_order SET order_status="Done", read_status="Read" WHERE username = %s AND number = %s', (username, number))
        self.connection.commit()

    def cancel_order_user(self, username):
        self.cursor.execute("UPDATE tbl_order SET order_status = 'Canceled' WHERE order_status = 'Ongoing' and status='Waiting Sms' and username = %s", (username,))
        self.connection.commit()

    def get_quota(self, username):
        self.cursor.execute("SELECT quota FROM tbl_customer WHERE username = %s", (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_app_price(self, app_id):
        self.cursor.execute("SELECT cost FROM tbl_application WHERE id = %s", (app_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def reduce_quota(self, username):
        self.cursor.execute("UPDATE tbl_customer SET quota = quota - 1 WHERE username = %s", (username,))
        self.connection.commit()
    
    def clean_order_user(self, username):
        self.cursor.execute("UPDATE tbl_order SET order_status = 'Canceled' WHERE `status` like '%Timeout%' and order_status = 'Ongoing' AND username = %s", (username,))
        self.connection.commit()
        
    def generate_random_string_password(self,length):
        characters = string.ascii_uppercase + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def add_quota(self, username, quantity):
        password = self.generate_random_string_password(4)
        self.cursor.execute("INSERT INTO tbl_customer (username, quota, password, email) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE quota = quota + %s",
                            (username, quantity, password, username + "@myotp.com", quantity))
        self.connection.commit()

    def delete_quota(self, username):
        self.cursor.execute("UPDATE tbl_customer SET quota = 0 WHERE username = %s", (username,))
        self.connection.commit()

    def __del__(self):
        self.cursor.close()
        self.connection.close()
        print("MySQL connection closed")