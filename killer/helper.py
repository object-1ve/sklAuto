import requests
import execjs
from bs4 import BeautifulSoup
import config
# 登录次数过多会封号半小时
def get_execution_salt(a):
    soup = BeautifulSoup(a, 'lxml')
    pwd_encrypt_salt_input = soup.find('input', {'id': 'pwdEncryptSalt'})
    execution_input = soup.find('input', {'name': 'execution'})
    execution_value = execution_input.get('value')
    salt_value = pwd_encrypt_salt_input.get('value')
    return execution_value,salt_value


def get_token(id_,pwd_):
    url = "https://authserver.zjnu.edu.cn/authserver/login?service=http%3A%2F%2Fskl.zjnu.edu.cn%2Fskl%2Fcas%2Flogin"
    params = {
        "service": "http://skl.zjnu.edu.cn/skl/cas/login"
    }
    response = requests.get(url,params=params)
    cookies_str = '; '.join([f"{cookie.name}={cookie.value}" for cookie in response.cookies])
    cookies_str_ = cookies_str+";"
    execution, salt = get_execution_salt(response.text)
    with open(config.SKL_ENCODE_PATH, "r", encoding="utf-8") as f:
        js_code = f.read()
    node = execjs.get()
    ctx = node.compile(js_code)
    pwd = pwd_
    password = ctx.call("encryptPassword", pwd, salt)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'{cookies_str_} org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN;',
        'Host': 'authserver.zjnu.edu.cn',
        'Origin': 'https://authserver.zjnu.edu.cn',
        'Referer': 'https://authserver.zjnu.edu.cn/authserver/login?service=http%3A%2F%2Fskl.zjnu.edu.cn%2Fskl%2Fcas%2Flogin',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    data = {
        "username":f"{id_}",
        "password": f"{password}",
        "captcha":"",
        "_eventId": "submit",
        "cllt": "userNameLogin",
        "dllt": "generalLogin",
        "lt":"",
        "execution": f"{execution}"
    }

    url = "https://authserver.zjnu.edu.cn/authserver/login?service=http%3A%2F%2Fskl.zjnu.edu.cn%2Fskl%2Fcas%2Flogin"
    # 发送POST请求
    response = requests.post(url=url, headers=headers, data=data, allow_redirects=True)

    final_url = response.url
    headers_ = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'skl.zjnu.edu.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
    }
    response1 = requests.get(final_url,headers=headers_,allow_redirects=True)
    final_url = response1.url
    token = final_url.split("token=")
    print()
    # print("token =",token[1])
    return token[1]