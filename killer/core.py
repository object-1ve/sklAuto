import time
import aiohttp
import asyncio
import sys
import requests
import json
# import important.function.get_token as get_token
from datetime import datetime, timedelta
import random
import pymysql
import uuid
from .client import sklZJNUClient
from tools import logger
import config
class sklZJNU():
    def beforeStart(self,user_id):
        # print("first: "+config.USER_ID, config.PASSWORD, config.DIFFERENCE)
        user = user_id
        try:
            with open("./config/json_config.json", "r", encoding="utf-8") as f:
                config_json = json.load(f)
                tmp = config_json[user]
                # print(json.dumps(tmp, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
        config.USER_ID = user
        config.PASSWORD = tmp['PASSWORD']
        config.DIFFERENCE = tmp['DIFFERENCE']
        config.AUTHORIZATION = tmp["AUTHORIZATION"]
        # print("second: "+config.USER_ID, config.PASSWORD, config.DIFFERENCE)
        with open('./config/json_config.json', 'w', encoding='utf-8') as file:
            json.dump(config_json, file, indent=4, ensure_ascii=False)
        logger.debug(f'user: {config.USER_ID}, password: {config.PASSWORD}, dif: {config.DIFFERENCE}')
        
    # 签到主程序
    def start(self):
        logger.info("model: cycle")
        client = sklZJNUClient()
        asyncio.run(client.run_next())
        return None
    # 测试连接
    def test_connection(self):
        client = sklZJNUClient()
        if client.test_connection():
            logger.debug("Connection successful")
        else:
            logger.error("Connection failed")
    # 获取今日课表
    def obtain_course_schedule_today(self):
        if config.AUTHORIZATION:
            client = sklZJNUClient()
            tmp = client.obtain_course_schedule_today(authorization=config.AUTHORIZATION)
        else:
            client = sklZJNUClient()
            tmp = client.obtain_course_schedule_today()
        # print(tmp)
        # logger.debug(tmp)
        # return tmp
        return None
    # 获取本周课表
    def obtain_course_schedule_week(self)->None:
        client = sklZJNUClient()
        if config.AUTHORIZATION:
            tmp = client.obtain_course_schedule_week(authorization=config.AUTHORIZATION)
        else:
            tmp = client.obtain_course_schedule_week()
        logger.debug(tmp)
        return None
    # 获取签到记录
    def obtain_check_in_records(self):
        client = sklZJNUClient()
        client.obtain_check_in_records()
        
    def test_authorization(self):
        client = sklZJNUClient()
        client.test_authorization()
    def just_run(self):
        client = sklZJNUClient()
        client.just_run()
    # def print_pretty_response(self, response_text):
    #     try:
    #         response_json = json.loads(response_text)
    #         pretty_response = json.dumps(response_json, indent=4, ensure_ascii=False)
    #         print(pretty_response)
    #     except json.JSONDecodeError:
    #         print("Response is not valid JSON")
    #         print(response_text)
    # def start_next():
        

        
        
        
