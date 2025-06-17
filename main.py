import requests
import json
import time
import sys
from datetime import datetime
from playsound3 import playsound
from playsound3.playsound3 import PlaysoundException
from winotify import Notification

CONFIG_FILE = "config.json"
SPECIAL_USERS_FILE = "Autopatrolled_user.json"
SOUND_FILE = "sound.mp3"
WIKI_BASE_URL = "https://zh.minecraft.wiki"
WIKI_API_URL = WIKI_BASE_URL + "/api.php"

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

LOG_TYPE_MAP = {
    "newusers": "用户创建",
    "delete": "删除",
    "block": "封禁",
    "protect": "保护",
    "abusefilter": "滥用过滤器",
    "rights": "用户权限",
    "upload": "上传",
    "move": "移动",
    "renameuser": "用户更名"
}

LOG_ACTION_MAP = {
    "create": "创建",
    "upload": "上传",
    "delete": "删除",
    "move": "移动",
    "overwrite": "覆盖上传",
    "block": "封禁",
    "reblock": "更改封禁",
    "unblock": "解除封禁",
    "move_prot": "移动保护设置",
    "protect": "保护",
    "unprotect": "移除保护",
    "modify": "修改",
    "create2": "登录状态创建账号",
    "byemail": "登录状态创建账号2",
    "migrated": "迁移",
    "rights": "权限更改",
    "revert": "恢复至旧版本",
    "restore": "还原修订版本",
    "event": "更改日志可见性",
    "renameuser": "重命名用户"
}

MESSAGE_TEMPLATES = {
    "log": {
        "upload": "（{magenta}上传日志{reset}）{time}，{user}对{title}执行了{action}操作，摘要为{comment}。",
        "move": "（{magenta}移动日志{reset}）{time}，{user}移动页面{title}至{target_title}，摘要为{comment}。",
        "renameuser": "（{magenta}用户更名日志{reset}）{time}，{user}重命名用户{olduser}为{newuser}，摘要为{comment}。",
        "default": "（{magenta}{log_type}日志{reset}）{time}，{user}对{title}执行了{action}操作，摘要为{comment}。"
    },
    "edit": "{time}，{user}在{title}做出编辑，字节更改为{length_diff}，摘要为{comment}。",
    "new": "{time}，{user}创建{title}，字节更改为{length_diff}，摘要为{comment}。"
}

TOAST_TEMPLATES = {
    "log": {
        "upload": "（上传日志）{user}对{title}执行了{action}操作，摘要为{comment}。",
        "move": "（移动日志）{user}移动页面{title}至{target_title}，摘要为{comment}。",
        "renameuser": "（用户更名日志）{user}重命名用户{olduser}为{newuser}，摘要为{comment}。",
        "default": "（{log_type}日志）{user}对{title}执行了{action}操作，摘要为{comment}。"
    },
    "edit": "{user}在{title}做出编辑，字节更改为{length_diff}，摘要为{comment}。",
    "new": "{user}创建{title}，字节更改为{length_diff}，摘要为{comment}。"
}

def generate_messages(data): # 生成控制台消息和弹窗消息文本
    base_params = {
        "time": format_timestamp(data['timestamp']),
        "user": data['user'],
        "title": data['title'],
        "comment": data['comment'],
    }
    if data['type'] == 'log' and data['logtype'] == 'move':
        base_params["target_title"] = data['logparams']['target_title']
    elif data['type'] == 'log' and data['logtype'] == 'renameuser':
        base_params["olduser"] = data['logparams']['olduser']
        base_params["newuser"] = data['logparams']['newuser']

    console_params = base_params.copy()
    console_params.update({
        "user": format_user(base_params["user"]),
        "title": f"{Colors.BLUE}{base_params['title']}{Colors.RESET}",
        "comment": format_comment(base_params['comment']),
        "magenta": Colors.MAGENTA,
        "reset": Colors.RESET
    })

    toast_params = base_params.copy()
    toast_params.update({
        "comment": "（空）" if base_params['comment'] == "" else base_params['comment']
    })

    if data['type'] == 'log':
        log_type = LOG_TYPE_MAP.get(data['logtype'], data['logtype'])
        action = LOG_ACTION_MAP.get(data['logaction'], data['logaction'])

        console_params.update({
            "log_type": log_type,
            "action": f"{Colors.MAGENTA}{action}{Colors.RESET}"
        })
        if data['logaction'] == 'move':
            console_params.update({
                "target_title": f"{Colors.BLUE}{console_params["target_title"]}{Colors.RESET}"
            })
        elif data['logaction'] == 'renameuser':
            console_params.update({
                "olduser": f"{Colors.BLUE}{console_params["olduser"]}{Colors.RESET}",
                "newuser": f"{Colors.BLUE}{console_params["newuser"]}{Colors.RESET}"
            })

        template_key = data['logtype'] if data['logtype'] in MESSAGE_TEMPLATES["log"] else "default"
        console_msg = MESSAGE_TEMPLATES["log"][template_key].format(**console_params)

        toast_params.update({
            "log_type": log_type,
            "action": action
        })
        toast_msg = TOAST_TEMPLATES["log"][template_key].format(**toast_params)
    else:
        console_params["length_diff"] = f"{Colors.MAGENTA}{format_length_diff(data['newlen'], data['oldlen'])}{Colors.RESET}"
        console_msg = MESSAGE_TEMPLATES[data['type']].format(**console_params)

        toast_params["length_diff"] = format_length_diff(data['newlen'], data['oldlen'])
        toast_msg = TOAST_TEMPLATES[data['type']].format(**toast_params)

    return console_msg, toast_msg

def generate_url(data): # 生成url
    if data['type'] == 'log':
        if data['logtype'] in ["upload", "move"]:  # 只有上传日志和移动日志具备有效revid值
            return f"{WIKI_BASE_URL}/?diff={data['revid']}"
        else:
            return f"{WIKI_BASE_URL}/Special:%E6%97%A5%E5%BF%97/{data['logtype']}"
    else:
        return f"{WIKI_BASE_URL}/?diff={data['revid']}"

def notification(msg_body,url): # 产生弹窗通知
    toast = Notification(
        app_id="Minecraft Wiki RecentChanges Monitor",
        title="",
        msg=msg_body
    )
    toast.add_actions(label="打开网页", launch=url)
    toast.show()
    sound_play()

def sound_play(): # 播放音效
    try:
        playsound(f"{SOUND_FILE}", block=False)
    except PlaysoundException:
        pass

def format_timestamp(timestamp_str): # 将UTC时间改为UTC+8
    time_part = timestamp_str[11:19]
    hour = int(time_part[0:2])
    hour = (hour + 8) % 24
    return f"{Colors.CYAN}{hour:02d}{time_part[2:]}{Colors.RESET}"

def format_comment(comment): # 摘要为空时输出（空）
    return f"（空）" if comment == "" else f"{Colors.CYAN}{comment}{Colors.RESET}"

def format_user(user): # 有巡查豁免权限的用户标记为绿色
    return f"{Colors.GREEN}{user}{Colors.RESET}" if user in special_users else f"{Colors.BLUE}{user}{Colors.RESET}"

def format_length_diff(newlen, oldlen): # 字节数变化输出和mw一致
    diff = newlen - oldlen
    return f"+{diff}" if diff > 0 else f"{diff}"

def print_rc(new_data): # 处理数据
    for data in new_data:
        console_msg, toast_msg = generate_messages(data)
        url = generate_url(data)

        print(console_msg)
        print(f"（{Colors.YELLOW}{url}{Colors.RESET}）")
        if data['type'] == "log" and data['logtype'] == "upload" and data['user'] not in special_users:
            print(f"（特殊巡查：{WIKI_BASE_URL}/index.php?curid={data['pageid']}&action=markpatrolled&rcid={data['rcid']}）")
        print("")

        if data['user'] not in special_users: # 无巡查豁免权限用户执行操作才出现弹窗
            notification(toast_msg, url)

def call_api(params): # 从Mediawiki API获取数据
    tries = 0
    while 1:
        try:
            # 发送 API 请求
            response = session.post(WIKI_API_URL, data=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            tries += 1
            if tries > 1:
                break

            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"（{current_time}）{Colors.RED}未获取到数据，20秒后重试。{Colors.RESET}", end='\n\n')
            toast = Notification(
                app_id="Minecraft Wiki RecentChanges Monitor",
                title="",
                msg="未获取到数据，20秒后重试。"
            )
            toast.show()
            sound_play()
            time.sleep(20)

    print(f"{Colors.RED}重试失败，请检查网络连接。{Colors.RESET}")
    toast = Notification(
        app_id="Minecraft Wiki RecentChanges Monitor",
        title="",
        msg="重试失败，请检查网络连接。"
    )
    toast.show()
    sound_play()
    input("按任意键退出")
    sys.exit(1)

# 读取配置文件
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)
    client_key = config["Client_application_key"]
    client_secret = config["Client_application_secret"]
    access_token = config["Access_token"]
    user_agent = config["User_Agent"]

# 获取巡查豁免权限用户列表
try:
    with open(SPECIAL_USERS_FILE, 'r', encoding='utf-8') as special_users_file:
        special_users = set(json.load(special_users_file))
except FileNotFoundError:
    print("巡查豁免权限用户列表获取失败", end='\n\n')
    special_users = set()

# 创建带认证头的会话
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {access_token}",
    "User-Agent": user_agent
})

rc_base_params = {
    "action": "query",
    "format": "json",
    "list": "recentchanges",
    "formatversion": "2",
    "rcprop": "user|title|timestamp|ids|loginfo|sizes|comment",
    "rcshow": "!bot",
    "rctype": "edit|new|log|external"
}

# 最近更改：不要获取机器人编辑，每次最多获取100个编辑
rc_params = rc_base_params.copy()
rc_params.update({"rclimit": "100"})

# 给第一次循环准备对比数据
inirial_rc_params = rc_base_params.copy()
inirial_rc_params.update({"rclimit": "1"})
initial_data = call_api(inirial_rc_params)
last_timestamp = initial_data['query']['recentchanges'][0]['timestamp']
last_rcid = initial_data['query']['recentchanges'][0]['rcid']

print("启动成功", end='\n\n')

while 1: # 主循环，每5秒获取一次数据
    time.sleep(5)

    current_rc_params = rc_params.copy()
    current_rc_params.update({"rcend": last_timestamp})
    current_data = call_api(current_rc_params)

    # 过滤出rcid大于last_rcid的新更改
    new_items = []
    for item in current_data['query']['recentchanges']:
        if item['rcid'] > last_rcid:
            new_items.append(item)

    if not new_items:
        continue

    last_timestamp = new_items[0]['timestamp']
    last_rcid = new_items[0]['rcid']

    new_items = new_items[::-1]

    print_rc(new_items)
