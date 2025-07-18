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
    "abusefilter": "滥用过滤器",
    "abusefilterblockeddomainhit": "被阻止的域名访问",
    "abusefilterprivatedetails": "abusefilterprivatedetails",
    "block": "封禁",
    "checkuser-temporary-account": "checkuser-temporary-account",
    "contentmodel": "内容模型更改",
    "create": "页面创建",
    "delete": "删除",
    "gblblock": "全域封禁",
    "gblrights": "全域权限历史记录", # 原文无“日志”两字
    "gloopcontrol": "gloopcontrol",
    "import": "导入",
    "managetags": "标签管理",
    "merge": "合并",
    "move": "移动",
    "newusers": "用户创建",
    "oath": "oath",
    "patrol": "巡查",
    "protect": "保护",
    "renameuser": "用户更名",
    "rights": "用户权限",
    "smw": "语义MediaWiki",
    "spamblacklist": "spamblacklist",
    "suppress": "suppress",
    "tag": "标签",
    "thanks": "感谢",
    "timedmediahandler": "TimedMediaHandler",
    "titleblacklist": "titleblacklist",
    "upload": "上传"
}

LOG_ACTION_MAP = {
    # abusefilter
    "create": "创建",
    "hit": "hit",
    "modify": "修改",
    # abusefilterblockeddomainhit（仅包含*）
    # abusefilterprivatedetails
    "access": "access",
    # block
    "block": "封禁",
    "reblock": "更改封禁设置",
    "unblock": "解封",
    # checkuser-private-event（仅包含*）
    # checkuser-temporary-account（仅包含*）
    # contentmodel
    "change": "内容模型的更改",
    "new": "使用非默认内容模型创建页面",
    # create
    '''"create": "",'''
    # delete
    "delete": "删除",
    "delete_redir": "通过覆盖删除重定向",
    "delete_redir2": "delete_redir2",
    "event": "更改日志事件的可见性",
    "restore": "还原页面",
    "revision": "更改页面版本的可见性",
    # gblblock
    "dwhitelist": "全域封禁白名单移除",
    "gblock": "全域封禁",
    "gblock2": "gblock2",
    "gunblock": "全域解封",
    '''"modify": "全域封禁修改",'''
    "whitelist": "全域封禁白名单添加",
    # gblrights
    '''"rights": "",'''
    # gloopcontrol（仅包含*）
    # import
    "interwiki": "跨wiki导入",
    '''"upload": "通过XML上传导入",'''
    # interwiki（仅包含*）
    # managetags
    "activate": "标签激活",
    '''"create": "标签创建",'''
    "deactivate": "标签取消激活",
    '''"delete": "标签删除",'''
    # merge
    "merge": "合并页面历史",
    # move
    "move": "移动页面",
    "move_redir": "移动页面覆盖重定向",
    # newusers
    "autocreate": "自动创建账号",
    "byemail": "创建账号并且密码已通过电子邮件发送",
    '''"create": "匿名用户创建账号",'''
    "create2": "注册用户创建账号",
    "migrated": "迁移账号",
    "newusers": "newusers",
    # oath（仅包含*）
    # patrol
    "autopatrol": "自动标记页面版本为已巡查",
    "patrol": "标记页面版本为已巡查",
    # protect
    '''"modify": "更改保护设定",'''
    "move_prot": "移动保护设置",
    "protect": "保护",
    "unprotect": "移除保护",
    # renameuser
    "renameuser": "重命名用户",
    # rights
    "autopromote": "autopromote",
    "blockautopromote": "禁止获得自动授权",
    "restoreautopromote": "允许获得自动授权",
    "rights": "更改用户组",
    # spamblacklist（仅包含*）
    # suppress
    '''"block": "",'''
    '''"delete": "",'''
    '''"event": "",'''
    "hide-afl": "hide-afl",
    '''"reblock": "",'''
    '''"revision": "",'''
    "unhide-afl": "unhide-afl",
    # tag
    "update": "向修订版本添加标签",
    # thanks（仅包含*）
    # timedmediahandler
    "resettranscode": "重置转码",
    # titleblacklist（仅包含*）
    # upload
    "overwrite": "覆盖上传",
    "revert": "回退至旧版本",
    "upload": "上传"
}

AF_ACTION_MAP = {
    "autocreateaccount": "自动创建账号",
    "createaccount": "创建账号",
    "delete": "删除",
    "edit": "编辑",
    "move": "移动",
    "stashupload": "stashupload",
    "upload": "上传文件"
}

AF_RESULT_MAP = {
    "": "无",
    "block": "封禁",
    "blockautopromote": "撤销自动确认",
    "blockautopromote,block": "撤销自动确认、封禁",
    "blockautopromote,rangeblock": "撤销自动确认、区段封禁",
    "blockautopromote,rangeblock,block": "撤销自动确认、区段封禁、封禁",
    "degroup": "从用户组移除",
    "disallow": "阻止",
    "rangeblock": "区段封禁",
    "rangeblock,block": "区段封禁、封禁",
    "tag": "标签",
    "throttle": "频率控制",
    "warn": "警告"
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

def generate_rc_messages(data): # 最近更改：生成控制台消息和弹窗消息文本
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
        app_id="Minecraft Wiki Admin Monitor",
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

def print_rc(new_data): # 处理最近更改数据
    for data in new_data:
        console_msg, toast_msg = generate_rc_messages(data)
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
    while True:
        try:
            # 发送API请求
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
                app_id="Minecraft Wiki Admin Monitor",
                title="",
                msg="未获取到数据，20秒后重试。"
            )
            toast.show()
            sound_play()
            time.sleep(20)

    print(f"{Colors.RED}重试失败，请检查网络连接。{Colors.RESET}")
    toast = Notification(
        app_id="Minecraft Wiki Admin Monitor",
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
    Access_token = config["Access_token"]
    User_Agent = config["User_Agent"]

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
    "Authorization": f"Bearer {Access_token}",
    "User-Agent": User_Agent
})

# 最近更改：不要获取机器人编辑，每次最多获取100个编辑
rc_params = {
    "action": "query",
    "format": "json",
    "list": "recentchanges",
    "formatversion": "2",
    "rcprop": "user|title|timestamp|ids|loginfo|sizes|comment",
    "rcshow": "!bot",
    "rctype": "edit|new|log|external",
    "rclimit": "100"
}

# 滥用日志：每次最多获取100条记录
afl_params = {
    "action": "query",
    "format": "json",
    "list": "abuselog",
    "formatversion": "2",
    "aflprop": "user|title|action|result|timestamp|revid|filter|ids",
    "afllimit": "100"
}

# 给第一次循环准备对比数据
initial_rc_params = rc_params.copy()
initial_rc_params.update({
    "rclimit": "1",
    "rcprop": "timestamp|ids"
})
initial_rc_data = call_api(initial_rc_params)
last_rc_timestamp = initial_rc_data['query']['recentchanges'][0]['timestamp']
last_rcid = initial_rc_data['query']['recentchanges'][0]['rcid']

initial_afl_params = afl_params.copy()
initial_afl_params.update({
    "afllimit": "1",
    "aflprop": "ids|timestamp"
})
initial_afl_data = call_api(initial_afl_params)
last_afl_timestamp = initial_afl_data['query']['abuselog'][0]['timestamp']
last_afl_id = initial_afl_data['query']['abuselog'][0]['id']

print("启动成功", end='\n\n')

while 1: # 主循环，每5秒获取一次最近更改和滥用日志数据
    time.sleep(5)

    current_rc_params = rc_params.copy()
    current_rc_params.update({"rcend": last_rc_timestamp})
    current_rc_data = call_api(current_rc_params)

    # 过滤出rcid大于last_rcid的新更改
    new_rc_items = []
    for rc_item in current_rc_data['query']['recentchanges']:
        if rc_item['rcid'] > last_rcid:
            new_rc_items.append(rc_item)

    current_afl_params = afl_params.copy()
    current_afl_params.update({"aflend": last_afl_timestamp})
    current_afl_data = call_api(current_afl_params)

    # 过滤出id大于last_afl_id的新滥用日志
    new_afl_items = []
    for afl_item in current_afl_data['query']['abuselog']:
        if afl_item['id'] > last_afl_id:
            new_afl_items.append(afl_item)

    if new_rc_items:
        last_rc_timestamp = new_rc_items[0]['timestamp']
        last_rcid = new_rc_items[0]['rcid']

        new_rc_items = new_rc_items[::-1]

    if new_afl_items:
        last_afl_timestamp = new_afl_items[0]['timestamp']
        last_afl_id = new_afl_items[0]['id']

        new_afl_items = new_afl_items[::-1]

        # print_afl(new_afl_items)

    print_rc(new_rc_items)
