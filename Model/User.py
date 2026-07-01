from tools import logger as logger
from DB.mysql import Mysql
class User():
    tablename = "skl_next"
    def __init__(self,username,password="",difference=0,authorization=""):
        self.username = username
        self.password = password
        self.difference = difference
        self.authorization = authorization
        return None
    def display_attributes(self):
        print("Username: ",self.username)
        print("Password: ",self.password)
        print("Difference: ",self.difference)
        print("Authorization: ",self.authorization)
        return None
    def update_authorization(self,new_auth):
        with Mysql() as mysql:
            sql = "UPDATE " + self.tablename + " SET " + "authorization = " + new_auth + " WHERE username = " + self.username
            result = mysql.execute(sql)
            logger.debug(result)
    def get(self):
        with Mysql() as mysql:
            sql = "SELECT * FROM " + self.tablename + " WHERE username = " + self.username
            result = mysql.execute(sql)
            # logger.debug(result)
            if len(result) == 1:
                self.username = result[0][0]
                self.password = result[0][1]
                self.difference = result[0][2]
                self.authorization = result[0][3]
                self.display_attributes()
                return True
            else:
                logger.debug("failed: something wrong")
                return False
    