# mcwzh-admin-monitor
此程序用于自动获取中文Minecraft Wiki最近更改和滥用日志的新内容。

The program automatically gets new content in RecentChanges and AbuseLogs of the Chinese Minecraft Wiki.

## 用途
每5秒尝试获取一次中文Minecraft Wiki最近更改和滥用日志的变化情况，新更改内容在Windows终端输出。如果是无巡查豁免权限的用户产生的，或是触发了70号过滤器“标记删除请求”，还会产生通知弹窗并播放音效。

程序会将单次操作产生的多个滥用日志项合并输出。程序会将对应的最近更改和滥用日志合并输出。

## 运作方式
在查询最近更改的链接后添加`&rcend=<时间戳>`可以获取自指定时间戳开始的所有内容。因此，程序每次获取内容都存储最新内容的时间戳和rcid，然后根据时间戳指定获取的数据，再根据rcid筛选出新内容，经过一系列处理后输出。滥用日志同理。

有时候，单次操作会同时触发多个滥用过滤器并产生多个滥用日志。程序会检查获取到的滥用日志是否有一致的用户、页面标题、时间戳，并将满足条件的多项滥用日志合并为一项。

有时候，执行成功的操作同时也会触发滥用过滤器。这样，API返回的滥用日志结果中会有`revid`字段，和其对应的最近更改项的`revid`一致。程序会将这两项合并为特殊的最近更改项，并在输出函数中检测，若满足条件则增加一条触发了滥用过滤器的备注。

## 使用方法
程序需要同目录存在`config.json`才能正常运作：
* 请自行按[MediaWiki文档要求](https://www.mediawiki.org/wiki/API:Etiquette#The_User-Agent_header)填写用户代理`user_agent`。
* 在这之前你应该需要先在[[Special:机器人密码]]创建一个机器人并获得密码，然后填入`username`和`password`。
* `RC_SOUND_FILE`、`AFL_SOUND_FILE`和`WARN_SOUND_FILE`用于指定产生弹窗时播放什么音效，这三项对应最近更改、滥用日志和程序的警告信息。可以是同目录下文件名或完整文件路径（JSON要求对反斜杠转义，不过也是可以正常解析路径的）。这些项为选填，不填就不会播放音效。

程序需要同目录存在`Autopatrolled_user.json`，作为有巡查豁免权限用户的列表。若不存在，只会在后台输出提示，然后所有用户均视为无巡查豁免权限。

## 注意事项
* 在中文Minecraft Wiki，只有巡查员及以上用户才能查询滥用日志。无此权限的用户请改为使用[mcwzh-rc-monitor](https://github.com/AblazeVase69188/mcwzh-rc-monitor)。
* 程序仅在Windows 11上可用（其实只是我没在Windows 10上面测试过而已）。
* 如果5秒内的最近更改新内容大于100条 ~~（应该不会这么多，CATS点两下才100条）~~，程序只会处理最新的100条。

## 授权协议
程序采用与Minecraft Wiki相同的CC BY-NC-SA 3.0协议授权。
