import requests
import json
import time
import sys
from datetime import datetime
from playsound3 import playsound, playsound3
from winotify import Notification

CONFIG_FILE = "config.json"
SPECIAL_USERS_FILE = "Autopatrolled_user.json"
WIKI_BASE_URL = "https://zh.minecraft.wiki/"
WIKI_API_URL = WIKI_BASE_URL + "api.php"
WIKI_DIFF_URL = WIKI_BASE_URL + "?diff="
WIKI_LOG_URL = WIKI_BASE_URL + "Special:Log/"
WIKI_AFL_URL = WIKI_BASE_URL + "Special:AbuseLog/"

LOG_TYPE_MAP = {
    "abusefilter": "滥用过滤器日志",
    "abusefilterblockeddomainhit": "被阻止的域名访问日志",
    "abusefilterprivatedetails": "abusefilterprivatedetails日志",
    "block": "封禁日志",
    "checkuser-temporary-account": "checkuser-temporary-account日志",
    "contentmodel": "内容模型更改日志",
    "create": "页面创建日志",
    "delete": "删除日志",
    "gblblock": "全域封禁日志",
    "gblrights": "全域权限历史记录",
    "gloopcontrol": "gloopcontrol日志",
    "import": "导入日志",
    "managetags": "标签管理日志",
    "merge": "合并日志",
    "move": "移动日志",
    "newusers": "用户创建日志",
    "oath": "oath日志",
    "patrol": "巡查日志",
    "protect": "保护日志",
    "renameuser": "用户更名日志",
    "rights": "用户权限日志",
    "smw": "语义MediaWiki日志",
    "spamblacklist": "spamblacklist日志",
    "suppress": "suppress日志",
    "tag": "标签日志",
    "thanks": "感谢日志",
    "timedmediahandler": "TimedMediaHandler日志",
    "titleblacklist": "titleblacklist日志",
    "upload": "上传日志"
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

AF_RESULT_ORDER_MAP = [
    "blockautopromote,rangeblock,block",
    "blockautopromote,rangeblock",
    "blockautopromote,block",
    "blockautopromote",
    "rangeblock,block",
    "rangeblock",
    "block",
    "disallow",
    "throttle",
    "degroup",
    "warn"
    "tag",
    ""
]

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

            toast_notification("未获取到数据，20秒后重试。", "warn", False)
            current_time = datetime.now()
            print(f"（{current_time}）未获取到数据，20秒后重试。", end='\n\n')
            time.sleep(20)

    toast_notification("重试失败，请检查网络连接。", "warn", False)
    current_time = datetime.now()
    print(f"（{current_time}）重试失败，请检查网络连接。")
    input("按回车键退出")
    sys.exit(1)

def toast_notification(msg_str, sound_type, add_button=True, url=""): # 播放音效并产生弹窗通知
    try:
        if sound_type == "rc":
            playsound(RC_SOUND_FILE, block=False)
        elif sound_type == "afl":
            playsound(AFL_SOUND_FILE, block=False)
        elif sound_type == "warn":
            playsound(WARN_SOUND_FILE, block=False)
    except playsound3.PlaysoundException:
        pass

    toast = Notification(
        app_id="Minecraft Wiki Admin Monitor",
        title="",
        msg=msg_str
    )
    if add_button:
        toast.add_actions(label="查看详情", launch=url)
    toast.show()

def print_rc(item): # 打印最近更改内容
    console_str = ""
    toast_str = ""
    type = item['type']
    title = item['title']
    revid = item['revid']
    user = item['user']
    len_diff = adjust_length_diff(item['newlen'], item['oldlen'])
    timestamp = adjust_timestamp(item['timestamp'])
    comment = adjust_comment(item['comment'])

    if type == 'log':
        logtype = item['logtype']
        logaction = item['logaction']
        logtype_str = LOG_TYPE_MAP.get(logtype, logtype)
        logaction_str = LOG_ACTION_MAP.get(logaction, logaction)
        if logtype == 'move':
            target_title = item['logparams']['target_title']
            console_str += f"（移动日志）{timestamp}，{user}移动页面{title}至{target_title}，摘要为{comment}。\n"
            toast_str += f"（移动日志）{user}移动页面{title}至{target_title}，摘要为{comment}。"
        elif logtype == 'renameuser':
            olduser = item['logparams']['olduser']
            newuser = item['logparams']['newuser']
            console_str += f"（用户更名日志）{timestamp}，{user}重命名用户{olduser}为{newuser}，摘要为{comment}。\n"
            toast_str += f"（用户更名日志）{user}重命名用户{olduser}为{newuser}，摘要为{comment}。"
        else:
            console_str += f"（{logtype_str}）{timestamp}，{user}对{title}执行了{logaction_str}操作，摘要为{comment}。\n"
            toast_str += f"（{logtype_str}）{user}对{title}执行了{logaction_str}操作，摘要为{comment}。"
    elif type == 'edit':
        console_str += f"{timestamp}，{user}在{title}做出编辑，字节更改为{len_diff}，摘要为{comment}。\n"
        toast_str += f"{user}在{title}做出编辑，字节更改为{len_diff}，摘要为{comment}。"
    elif type == 'new':
        console_str += f"{timestamp}，{user}创建{title}，字节更改为{len_diff}，摘要为{comment}。\n"
        toast_str += f"{user}创建{title}，字节更改为{len_diff}，摘要为{comment}。"

    if 'id' in item:
        result = item['result']
        filter = item['filter']
        result_str = AF_RESULT_MAP.get(result, result)
        console_str += f"此操作触发了过滤器。采取的行动：{result_str}；过滤器描述：{filter}。\n"
        toast_str += f"\n此操作触发了过滤器：{filter}。"

    if revid == 0:
        url = f"{WIKI_LOG_URL}{item['logtype']}"
    else:
        url = f"{WIKI_DIFF_URL}{revid}"

    console_str += f"{url}\n"

    if type == 'log' and logtype == 'upload':
        console_str += f"特殊巡查：{WIKI_BASE_URL}?curid={item['pageid']}&action=markpatrolled&rcid={item['rcid']}\n"

    if user not in special_users or item.get('filter_id') == 70: # 用户的编辑需要巡查，或者这是标记删除请求的编辑
        toast_notification(toast_str, "rc", url=url)
    print(console_str)

def print_afl(item): # 打印滥用日志内容
    console_str = ""
    toast_str = ""
    id = item['id']
    filter = item['filter']
    user = item['user']
    title = item['title']
    action = item['action']
    result = item['result']
    timestamp = adjust_timestamp(item['timestamp'])
    action_str = AF_ACTION_MAP.get(action, action)
    result_str = AF_RESULT_MAP.get(result, result)
    url = f"{WIKI_AFL_URL}{id}"

    console_str += f"{timestamp}，{user}在{title}执行操作“{action_str}”时触发了过滤器。采取的行动：{result_str}；过滤器描述：{filter}。\n"
    toast_str += f"{user}在{title}执行操作“{action_str}”时触发了过滤器。采取的行动：{result_str}；过滤器描述：{filter}。"

    console_str += f"{url}\n"

    if user not in special_users:
        toast_notification(toast_str, "afl", url=url)
    print(console_str)

def adjust_timestamp(timestamp_str): # 移除日期部分、调整时间戳至UTC+8
    time_part = timestamp_str[11:19]
    hour = int(time_part[0:2])
    hour = (hour + 8) % 24
    return f"{hour:02d}{time_part[2:]}"

def adjust_comment(comment): # 摘要为空时输出（空）
    return f"（空）" if comment == "" else comment

def adjust_length_diff(newlen, oldlen): # 字节数变化输出和MediaWiki一致
    diff = newlen - oldlen
    return f"+{diff}" if diff > 0 else diff

# 加载配置
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)
    user_agent = config["user_agent"]
    username = config["username"]
    password = config["password"]
    RC_SOUND_FILE = config["RC_SOUND_FILE"]
    AFL_SOUND_FILE = config["AFL_SOUND_FILE"]
    WARN_SOUND_FILE = config["WARN_SOUND_FILE"]

# 获取巡查豁免权限用户列表
try:
    with open(SPECIAL_USERS_FILE, 'r', encoding='utf-8') as special_users_file:
        special_users = set(json.load(special_users_file))
except FileNotFoundError:
    print("巡查豁免权限用户列表获取失败", end='\n\n')
    special_users = set()

# 创建会话
session = requests.Session()
session.headers.update({"User-Agent": user_agent})

# 获取登录令牌
try:
    login_token_response = session.get(WIKI_API_URL, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    })
    login_token_response.raise_for_status()
    login_token_data = login_token_response.json()
    print("登录令牌获取成功")
except Exception as e:
    print("登录令牌获取异常：", e)
    input("按回车键退出")
    sys.exit(1)

login_token = login_token_data['query']['tokens']['logintoken']

# 登录
try:
    login_response = session.post(WIKI_API_URL, data={
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": login_token,
        "format": "json"
    })
    login_response.raise_for_status()
    login_data = login_response.json()
except Exception as e:
    print("登录请求异常：", e)
    input("按回车键退出")
    sys.exit(1)

if login_data['login']['result'] == 'Success':
    print("登录成功")
else:
    print("登录失败：", login_data['login'])
    input("按回车键退出")
    sys.exit(1)

query_params = {
    "action": "query",
    "format": "json",
    "list": "recentchanges|abuselog",
    "formatversion": 2,
    "rcprop": "title|timestamp|ids|comment|user|loginfo|sizes",
    "rcshow": "!bot",
    "rclimit": 100,
    "rctype": "edit|new|log",
    "afllimit": 100,
    "aflprop": "ids|user|title|action|result|timestamp|revid|filter",
}

# 准备初始数据
initial_params = query_params.copy()
initial_params.update({
    "rcprop": "timestamp|ids",
    "rclimit": 1,
    "afllimit": 1,
    "aflprop": "ids|timestamp"
})

initial_data = call_api(initial_params)

last_rc_timestamp = initial_data["query"]["recentchanges"][0]["timestamp"]
last_rcid = initial_data["query"]["recentchanges"][0]["rcid"]
last_afl_timestamp = initial_data["query"]["abuselog"][0]["timestamp"]
last_afl_id = initial_data["query"]["abuselog"][0]["id"]

print("启动成功", end='\n\n')

time.sleep(5)
interval = 5
next_run = time.monotonic()

# 主循环
while True:
    query_params.update({
        "rcend": last_rc_timestamp,
        "aflend": last_afl_timestamp
    })

    current_data = call_api(query_params)
    # API默认返回的顺序是新的在前，旧的在后，所以需要反转

    new_rc_items = []
    for rc_item in reversed(current_data["query"]["recentchanges"]):
        if rc_item["rcid"] > last_rcid:
            new_rc_items.append(rc_item)

    new_afl_items = []
    for afl_item in reversed(current_data["query"]["abuselog"]):
        if afl_item["id"] > last_afl_id:
            new_afl_items.append(afl_item)

    is_new_rc = 0
    is_new_afl = 0

    if new_rc_items:
        is_new_rc = 1
        last_rc_timestamp = new_rc_items[-1]['timestamp']
        last_rcid = new_rc_items[-1]['rcid']

    if new_afl_items:
        is_new_afl = 1
        last_afl_timestamp = new_afl_items[-1]['timestamp']
        last_afl_id = new_afl_items[-1]['id']

        # 合并单次操作产生的多个滥用日志项
        merged_afl_items = []
        # 仅检测用户、页面标题、时间戳是否一致
        groups = {}
        for afl_item in new_afl_items:
            key = (afl_item["user"], afl_item["title"], afl_item["timestamp"])
            if key not in groups:
                groups[key] = []
            groups[key].append(afl_item)

        for key, items in groups.items():
            if len(items) == 1:
                merged_afl_items.append(items[0])
            else:
                filters = [item["filter"] for item in items]
                results = [item["result"] for item in items]

                selected_result = ",".join(results)
                for result in AF_RESULT_ORDER_MAP:
                    if result in results:
                        selected_result = result
                        break

                # 包含全部过滤器名称和最高级别的操作名称
                merged_item = items[0].copy()
                merged_item["filter"] = "、".join(filters)
                merged_item["result"] = selected_result
                merged_afl_items.append(merged_item)

        new_afl_items = merged_afl_items

    # 调试打印内容：https://zh.minecraft.wiki/w/Special:API%E6%B2%99%E7%9B%92#action=query&format=json&list=recentchanges%7Cabuselog&formatversion=2&rcprop=title%7Ctimestamp%7Cids%7Ccomment%7Cuser%7Cloginfo%7Csizes&rcshow=!bot&rclimit=1&rctype=log%7Cedit%7Cnew&afllimit=1&aflprop=ids%7Cuser%7Ctitle%7Caction%7Cresult%7Ctimestamp%7Crevid%7Cfilter
    if is_new_rc == 1 and is_new_afl == 0: # 仅最近更改
        for rc_item in new_rc_items:
            print_rc(rc_item)

    elif is_new_rc == 0 and is_new_afl == 1: # 仅滥用日志
        for afl_item in new_afl_items:
            print_afl(afl_item)

    elif is_new_rc == 1 and is_new_afl == 1: # 同时存在最近更改和滥用日志
        merged = []

        for rc_item in new_rc_items:
            merged.append(rc_item)
        for afl_item in new_afl_items:
            merged.append(afl_item)

        merged.sort(key=lambda x: x['timestamp'])

        i = 1 # 第一项一定是最近更改，或者是没有对应最近更改的滥用日志
        while i < len(merged): # 合并有对应最近更改的滥用日志至对应的最近更改项
            item = merged[i]
            if 'revid' in item and 'type' not in item: # 如果是滥用日志项且有revid（表示有对应的最近更改）
                merged[i-1] = {**merged[i-1], **item}
                # 移除已被合并的滥用日志项
                merged.pop(i)
                continue
            i += 1

        for merged_item in merged: # 最终输出
            if 'type' in merged_item:
                print_rc(merged_item)
            else:
                print_afl(merged_item)

    # 防止前面逻辑耗时过长，导致单次请求间隔超出5秒
    next_run += interval
    sleep_time = next_run - time.monotonic()
    if sleep_time > 0:
        time.sleep(sleep_time)
