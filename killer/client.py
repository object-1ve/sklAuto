import time
import aiohttp
import asyncio
import sys
import requests
import json
import pymysql
import uuid
import random
from datetime import datetime, timedelta
from .helper import get_token
import config
from tools import logger
from Model.User import User
class sklZJNUClient:


    def __init__(self):
        self.USER_ID = config.USER_ID
        self.PASSWORD = config.PASSWORD
        self.DIFFERENCE = config.DIFFERENCE
        self.file_path = config.SKL_PATH
        self.authorization = config.AUTHORIZATION
        self.next_time = datetime.now()
        self.Right_code = []
        self.Expired_code = []
        self.Code_status = set()
        self.header = self.get_default_header()
        self.data_file_path = config.DATA_FILE_PATH
        # self.expired_time = datetime.datetime.now()

    def get_default_header(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": "Bearer eyJ",
            "Connection": "keep-alive",
            "Host": "skl.zjnu.edu.cn",
            "Referer": "https://skl.zjnu.edu.cn/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090c0f) XWEB/11275 Flue",
            "wengine_vpn_ticketwebvpn_zjnu_edu_cn": "11111",
        }


    def set_authorization(self):
        token = get_token(self.USER_ID, self.PASSWORD)
        logger.info(f"update token {token}")
        self.authorization = "Bearer " + token


    def test_connection(self):
        try:
            token = get_token(self.USER_ID, self.PASSWORD)
            logger.info(f"update token {token}")
            logger.debug(token)
            return bool(token)
        except Exception as e:
            logger.error("wrong id or password: %s", e)
            return False
        
    def get_header(self):
        token = get_token(self.USER_ID, self.PASSWORD)
        logger.info(f"update token {token}")
        self.authorization = "Bearer " + token
        try:
            with open(self.data_file_path, 'r', encoding="utf-8") as file:
                config_json = json.load(file)
            with open('./config/json_config.json', 'w', encoding='utf-8') as file:
                config_json[self.USER_ID]["AUTHORIZATION"] = self.authorization
                json.dump(config_json, file, indent=4, ensure_ascii=False)
                logger.info(f"update authorization successfully: {self.authorization}")
        except Exception as e:
            logger.error("update data authorization error: %s", e)
            
        logger.info(self.authorization)
        headers = self.get_default_header()
        headers["Authorization"] = f"Bearer {token}"
        return headers
    

    def get_header_with_authorization(self):
        headers = self.get_default_header()
        headers["Authorization"] = self.authorization
        return headers


    def judge_go(self, str_="", flag: bool = False):
        payload = {
            "startDate": "2025-02-10",
            "endDate": "2025-08-01"
        }
        if flag:
            logger.debug(json.dumps(payload, indent=4, ensure_ascii=False))
        url_get_course = "http://skl.zjnu.edu.cn/skl/stat/stu/user"
        response = requests.get(url_get_course, headers=self.header, params=payload)
        if response.status_code != 200:
            logger.debug(f"now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} authorization is not valid")
            self.header = self.get_header()
            response = requests.get(url_get_course, headers=self.header, params=payload)
            if response.status_code != 200:
                logger.error("something wrong with authorization")
                import sys
                sys.exit()
        # logger.debug(response.text)
        # if response.text != []:
        #     # logger.debug("新学期快乐")
        #     right_count = 0
        #     total_count = 0
        # else:
        parsed_data = json.loads(response.text)
        if not parsed_data:
            return False
        right_count = parsed_data[0]['rightCount']
        total_count = parsed_data[0]['totalCount']
        if flag == False:
            print(f"\rright: {right_count} total: {total_count} now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", end='', flush=True)
        if flag:
            logger.debug(f"difference update successfully: former: {self.DIFFERENCE} now: {total_count - right_count}")
            try:
                with open(self.data_file_path, 'r', encoding="utf-8") as file:
                    config_json = json.load(file)
                with open('./config/json_config.json', 'w', encoding='utf-8') as file:
                    config_json[self.USER_ID]["DIFFERENCE"] = total_count - right_count
                    json.dump(config_json, file, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error("update data authorization error: %s", e)
            self.DIFFERENCE = total_count - right_count
        return total_count - right_count != self.DIFFERENCE
            
    def judge_token(self, interval):
        if datetime.now() >= self.next_time:
            self.next_time = datetime.now() + timedelta(seconds=interval)
            self.header = self.get_header()
            print(f"本次更新时间: {datetime.now()} 下次更新时间: {self.next_time} now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(2)
        time_interval = self.get_interval_time(datetime.now(), self.next_time)
        return f"距离下次获取token: {time_interval} ------ "
    
    
    def judge_token_next(self):
        if self.test_authorization() == False:
            self.header = self.get_header()

    def add_message(self, success_code, expired_code, type_):
        try:
            conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", charset="utf8", database='yzzob')
            cursor = conn.cursor()
            new_guid = str(uuid.uuid4())
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO skl (time, success, expired, type, user_id, uuid) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (now_time, success_code, expired_code, type_, self.USER_ID, new_guid)
            cursor.execute(sql, val)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print("Error:", e)
            return False


    async def process_code(self, session, code):
        params = {"code": code}
        async with session.get("http://skl.zjnu.edu.cn/skl/checkIn/valid-code", headers=self.header, params=params) as response:
            if response.headers.get('Content-Type', '').startswith('application/json'):
                # print(response.text)
                response_j = await response.json()
                if response_j["message"] == "签到码不正确":
                    # pass
                    print(f"\r {code} {response_j}",end="")
                else:
                    print()
                    print(f"{code} {response_j}")
                    print()
                # if code == "0000":
                #     print()
                #     print(f"start {code} {response_j}")
                # if code == "9999":
                #     print(f"finish {code} {response_j}")
                if 'message' in response_j:
                    if response_j['message'] == '签到成功':
                        self.Right_code.append(code)
                    elif response_j['message'] == '签到码过期':
                        self.Expired_code.append(code)
                    self.Code_status.add(response_j['message'])
            else:
                print(f"Response for code {code} is not JSON.")
                print(await response.text())  # 打印非JSON响应内容


    async def main(self):
        async with aiohttp.ClientSession() as session:
            print()
            logger.debug("签到中.......")
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                # logger.debug(self.header)
                tasks = [self.process_code(session, code.strip()) for code in lines]
                await asyncio.gather(*tasks)
        print()
        print(f"签到成功: {self.Right_code}")
        print(f"过期的签到码: {self.Expired_code}")
        print(f"签到码的返回种类: {self.Code_status}")
        self.add_message(' | '.join(self.Right_code), ' | '.join(self.Expired_code), ' | '.join(self.Code_status))
        for i in range(1, 20):
            print(f"还有 {20 - i} 秒睡眠")
            time.sleep(1)

                
    def run_next(self):
        self.header = self.get_default_header()
        self.header["Authorization"] = f"Bearer {self.authorization}"
        flag = True
        while True:
            # logger.debug("!")
            try:
                while True:
                    tmp = self.judge_go(flag=flag)
                    if flag:
                        flag = False
                    # logger.debug("!")
                    if tmp:
                    # if True:
                        # logger.debug("!")
                        asyncio.run(self.main())
                        logger.info("快看看签到了没^_^")
                    random_float_range = random.uniform(4, 6)
                    rounded_float_range = round(random_float_range, 3)
                    time.sleep(rounded_float_range)
                    
            except Exception as e:
                logger.debug(f"An error occurred: {e}")
                time.sleep(1)

    def obtain_course_schedule_today(self, authorization=None):
        if authorization:
            self.authorization = authorization
        else:
            if self.USER_ID and self.PASSWORD:
                self.set_authorization()
            if not self.USER_ID and not self.PASSWORD:
                logger.error("authorization is useless,so USER_ID and PASSWORD cannot be empty. Exiting the program.")
                sys.exit()
        headers = self.get_default_header()
        headers["Authorization"] = self.authorization
        url = "http://skl.zjnu.edu.cn/skl/course"
        params = {
            "startTime": f"{datetime.now().date()}",
            "type": "day"
        }
        response = requests.get(url, headers=headers, params=params, verify=False)
        a = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
        print(a)
        return None


    def obtain_course_schedule_week(self, authorization=None):
        now = datetime.now()
        if authorization:
            self.authorization = authorization
        else:
            if self.USER_ID and self.PASSWORD:
                self.set_authorization()
            if not self.USER_ID and not self.PASSWORD:
                logger.error("authorization is useless,so USER_ID and PASSWORD cannot be empty. Exiting the program.")
                sys.exit()
        dates = [datetime.now().date() + timedelta(days=i) for i in range(8)]
        results = ""
        for date in dates:
            date_o = (date.weekday() + 1) % 7
            if date_o == 0 or date_o == 1:
                continue
            headers = self.get_default_header()
            headers["Authorization"] = self.authorization
            url = "http://skl.zjnu.edu.cn/skl/course"
            params = {
                "startTime": f"{date}",
                "type": "day"
            }
            response = requests.get(url, headers=headers, params=params, verify=False)
            response_json = json.loads(response.text)
            response_json['course_date'] = str(date)
            results += json.dumps(response_json, indent=4, ensure_ascii=False)+"\n"
        return results
    
    
    def get_start_date_follow_obtain_check_in_records(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        if current_month <= 6:
            start_date = f"{current_year - 1}-01-20"
        else:
            start_date = f"{current_year}-08-20"
        return start_date
    
    
    def timestamp_to_date(self,timestamp_ms):
        timestamp_s = timestamp_ms / 1000
        date_time = datetime.fromtimestamp(timestamp_s)
        formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date_time
    
    def test_authorization(self):
        headers = self.get_default_header()
        with open("./config/json_config.json", "r", encoding="utf-8") as f:
            config_json = json.load(f)
        self.authorization = config_json[self.USER_ID]["AUTHORIZATION"]
        headers["Authorization"] = self.authorization
        url = "http://skl.zjnu.edu.cn/skl/course"
        params = {
            "startTime": f"{datetime.now().date()}",
            "type": "day"
        }
        response = requests.get(url, headers=headers, params=params, verify=False)
        # print(response.text)
        # print(response.status_code)
        if response.status_code == 200:
            return True
        else:
            return False
        
    
    def obtain_check_in_records(self):
        self.header = self.get_default_header()
        self.header["Authorization"] = f"Bearer {self.authorization}"
        url = "http://skl.zjnu.edu.cn/skl/check-in-student-detail/my"
        params = {
            "startDate": self.get_start_date_follow_obtain_check_in_records(),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.get(url, headers=self.header, params=params)
        if response.status_code != 200:
            self.header = self.get_header()
            response = requests.get(url, headers=self.header, params=params)
            if response.status_code != 200:
                logger.error("something wrong with authorization")
                import sys 
                sys.exit()
            else:
                self.update_json_information(authorization=self.authorization)
                return None
        response_json = json.loads(response.text)
        for item in response_json:
            item['createTime'] = self.timestamp_to_date(item['createTime'])
            item['recordDate'] = self.timestamp_to_date(item['recordDate'])
        pretty_response = json.dumps(response_json, indent=4, ensure_ascii=False)
        print(pretty_response)
        with open('text.json','w',encoding='utf-8') as f:
            f.write(pretty_response)
        return None
    
    def obtain_check_in_records_today(self):
        if config.AUTHORIZATION:
            self.authorization = config.AUTHORIZATION
        else:
            if self.USER_ID and self.PASSWORD:
                self.set_authorization()
            if not self.USER_ID and not self.PASSWORD:
                logger.error("USER_ID and PASSWORD cannot be empty. Exiting the program.")
                sys.exit()
        url = "http://skl.zjnu.edu.cn/skl/check-in-student-detail/my"
        params = {
            "startDate": datetime.now().strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        self.header = self.get_header_with_authorization()
        response = requests.get(url, headers=self.header, params=params)
        response_json = json.loads(response.text)
        for item in response_json:
            item['createTime'] = self.timestamp_to_date(item['createTime'])
            item['recordDate'] = self.timestamp_to_date(item['recordDate'])
        pretty_response = json.dumps(response_json, indent=4, ensure_ascii=False)
        logger.debug(pretty_response)
        return None
    def get_pretty_response(self, response_text):
        try:
            response_json = json.loads(response_text)
            pretty_response = json.dumps(response_json, indent=4, ensure_ascii=False)
            #print(pretty_response)
            return pretty_response
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print(response_text)
            return None
        
        
    def update_json_information(self,authorization="hah",difference=1000):
        with open("./config/json_config.json", "r", encoding="utf-8") as f:
            config_json = json.load(f)
        with open("./config/json_config.json", "w", encoding="utf-8") as f:
            if authorization!="hah":
                config_json[self.USER_ID]["AUTHORIZATION"] = authorization
                self.authorization = authorization
            else:
                logger.debug("authorization is not updated")
            if difference!=1000:
                logger.debug("difference: from %d to %d" % (config_json[self.USER_ID]["DIFFERENCE"],difference))
                config_json[self.USER_ID]["DIFFERENCE"] = difference
                self.DIFFERENCE = difference    
            else:
                logger.debug("difference is not updated")
            json.dump(config_json, f, indent=4, ensure_ascii=False)
            logger.debug("json file update successful! ")   
            
            
            
    def just_run(self):
        # logger.debug(f"user_id: {self.USER_ID} password: {self.PASSWORD} difference: {self.DIFFERENCE}")
        self.authorization = config.AUTHORIZATION
        self.header = self.get_header_with_authorization()
        # logger.debug(self.authorization)
        while True:
            try:
                while True:
                    if True:
                        asyncio.run(self.main())
                        print("快看看签到了没^_^")
                    random_float_range = random.uniform(4, 6)
                    rounded_float_range = round(random_float_range, 3)
                    time.sleep(rounded_float_range)
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(1)
                

        