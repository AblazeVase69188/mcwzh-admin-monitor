import sys
import requests
import pywikiapi as wiki
import time
import json
from datetime import datetime, timedelta

def format_timestamp(timestamp_str): # 将UTC时间改为UTC+8
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
    timestamp += timedelta(hours=8)
    return timestamp.strftime('%H:%M:%S')

def format_comment(comment): # 摘要为空时输出（空）而不是【】
    return "（空）" if comment == "" else f"【{comment}】"

def print_rc(new_data): # 解析新更改数据并输出
    if new_data:
        for item in new_data:
            length_difference = item['newlen'] - item['oldlen']
            formatted_time = format_timestamp(item['timestamp'])
            comment_display = format_comment(item['comment'])
            if item['type'] == 'log': # pycharm自动缩进有点难绷
                logtype_display = "用户创建" if item['logtype'] == "newusers" else \
                    "删除" if item['logtype'] == "delete" else \
                        "封禁" if item['logtype'] == "block" else \
                            "保护" if item['logtype'] == "protect" else \
                                "滥用过滤器" if item['logtype'] == "abusefilter" else \
                                    "用户权限" if item['logtype'] == "rights" else \
                                        "移动" if item['logtype'] == "move" else \
                                            item['logtype']
                logaction_display = "创建" if item['logaction'] == "create" else \
                    "上传" if item['logaction'] == "upload" else \
                        "删除" if item['logaction'] == "delete" else \
                            "移动" if item['logaction'] == "move" else \
                                "覆盖上传" if item['logaction'] == "overwrite" else \
                                    "封禁" if item['logaction'] == "block" else \
                                        "更改封禁" if item['logaction'] == "reblock" else \
                                            "解除封禁" if item['logaction'] == "unblock" else \
                                                "移动保护设置" if item['logaction'] == "move_prot" else \
                                                    "保护" if item['logaction'] == "protect" else \
                                                        "移除保护" if item['logaction'] == "unprotect" else \
                                                            "修改" if item['logaction'] == "modify" else \
                                                                "登录状态创建账号" if item['logaction'] == "create2" else \
                                                                    "登录状态创建账号2" if item['logaction'] == "byemail" else \
                                                                        "迁移" if item['logaction'] == "migrated" else \
                                                                            "权限更改" if item['logaction'] == "rights" else \
                                                                                "移动" if item['logaction'] == "move" else \
                                                                                    item['logaction']
                if item['logtype'] == "upload":
                    print(f"（上传日志）{formatted_time}，{item['user']}对{item['title']}执行了{logaction_display}操作，摘要为{comment_display}。（https://zh.minecraft.wiki/?diff={item['revid']}）（特殊巡查：https://zh.minecraft.wiki/index.php?curid={item['pageid']}&action=markpatrolled&rcid={item['rcid']}）")
                elif item['logtype'] == "move":
                    print(f"（移动日志）{formatted_time}，{item['user']}对{item['title']}执行了{logaction_display}操作，摘要为{comment_display}。（https://zh.minecraft.wiki/?diff={item['revid']}）")
                else:
                    print(f"（{logtype_display}日志）{formatted_time}，{item['user']}对{item['title']}执行了{logaction_display}操作，摘要为{comment_display}。")
            elif item['type'] == 'edit':
                print(f"{formatted_time}，{item['user']}在{item['title']}做出编辑，字节更改为{length_difference}，摘要为{comment_display}。（https://zh.minecraft.wiki/?diff={item['revid']}）（特殊巡查：https://zh.minecraft.wiki/index.php?curid={item['pageid']}&action=markpatrolled&rcid={item['rcid']}）")
            elif item['type'] == 'new':
                print(f"{formatted_time}，{item['user']}创建{item['title']}，字节更改为{length_difference}，摘要为{comment_display}。（https://zh.minecraft.wiki/?diff={item['revid']}）（特殊巡查：https://zh.minecraft.wiki/index.php?curid={item['pageid']}&action=markpatrolled&rcid={item['rcid']}）")
            elif item['type'] == 'external': # 未知类型，直接输出原文
                print(item)

def print_abuselog(new_log): # 解析新滥用日志并输出
    if new_log:
        for item in new_log:
            formatted_time = format_timestamp(item['timestamp'])
            if item['type'] == 'log':
                action_display = "编辑" if item['action'] == "edit" else \
                    "创建账号" if item['action'] == "createaccount" else \
                        "移动" if item['action'] == "move" else \
                            item['action']
                result_display = "警告" if item['result'] == "warn" else \
                    "标签" if item['result'] == "tag" else \
                        "无" if item['result'] == "" else \
                            "阻止" if item['result'] == "disallow" else \
                                "封禁" if item['result'] == "block" else \
                                    item['result']
                print(f"{formatted_time}，{item['user']}在{item['title']}执行{action_display}操作时触发了过滤器“{item['filter']}”。采取的行动：{result_display}（https://zh.minecraft.wiki/w/Special:%E6%BB%A5%E7%94%A8%E6%97%A5%E5%BF%97/{item['id']}）")

def get_data(api_url): # 从Mediawiki API获取数据
    try:
        response = requests.get(api_url,headers={"User-Agent": "AblazeVase69188's recent changes monitor (355846525@qq.com)"})
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException:
        print("未获取到数据，请检查API URL或网络连接。")
        sys.exit(1)

# 登录
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    username = config["username"]
    password = config["password"]
site = wiki.Site("https://zh.minecraft.wiki/api.php", retry_after_conn=30)
site.login(username, password)

# 最近更改：不要获取机器人编辑，每次获取25个编辑（SimpleBatchUpload大约每秒最多上传5个文件）；滥用日志：每次获取10个日志
rc_url = "https://zh.minecraft.wiki/api.php?action=query&format=json&list=recentchanges&formatversion=2&rcprop=user%7Ctitle%7Ctimestamp%7Cids%7Cloginfo%7Csizes%7Ccomment&rcshow=!bot&rclimit=25&rctype=edit%7Cnew%7Clog%7Cexternal"
abuselog_url = "https://zh.minecraft.wiki/api.php?action=query&format=json&prop=&list=abuselog&meta=&formatversion=2&afllimit=10&aflprop=ids%7Cuser%7Ctitle%7Caction%7Cresult%7Ctimestamp%7Cfilter"

# 给第一次循环准备对比数据
data1 = get_data(rc_url)
log1 = get_data(abuselog_url)

last_abuse_check = time.time() # 记录上次检查滥用日志的时间

while 1: # 主循环，每5秒获取一次最近更改数据，每30秒获取一次滥用日志数据
    time.sleep(5)
    current_time = time.time()
    data2 = get_data(rc_url)

    # 根据时间戳差异确定新增数据
    timestamps1 = [item['timestamp'] for item in data1['query']['recentchanges']]
    timestamps2 = [item['timestamp'] for item in data2['query']['recentchanges']]
    new_timestamps = [ts for ts in timestamps2 if ts not in timestamps1]
    new_data = [item for item in data2['query']['recentchanges'] if item['timestamp'] in new_timestamps]
    print_rc(new_data)
    data1 = data2

    if current_time - last_abuse_check >= 30:
        log2 = get_data(abuselog_url)

        # 根据时间戳差异确定新增滥用日志数据
        log_timestamps1 = [item['timestamp'] for item in log1['query']['abuselog']]
        log_timestamps2 = [item['timestamp'] for item in log2['query']['abuselog']]
        new_log_timestamps = [ts for ts in log_timestamps2 if ts not in log_timestamps1]
        new_log = [item for item in log2['query']['abuselog'] if item['timestamp'] in new_log_timestamps]
        print_abuselog(new_log)
        log1 = log2
        last_abuse_check = current_time
