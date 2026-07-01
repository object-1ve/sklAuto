from killer.core import sklZJNU
import json
from tools.log import logger
import config
from DB.mysql import Mysql
from Model.User import User
if __name__ == '__main__':
    user = "21221212"
    zjnu = sklZJNU()
    zjnu.beforeStart(user_id=user)
    # zjnu.test_authorization()
    # zjnu.start()
    zjnu.just_run() 
    # zjnu.obtain_check_in_records() 
    # zjnu.obtain_course_schedule_today()
    # zjnu.obtain_course_schedule_week()
    # zjnu.test_connection() 
    # with Mysql() as mysql:
    #     condition = 'username = %s'bb
    #     condition_params = config.USER_ID
    #     user = User(username=config.USER_ID)
    #     user.get() 
    #     zjnu = sklZJNU(user=user)   