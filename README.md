# mcwzh-admin-monitor
此程序用于自动获取中文Minecraft Wiki最近更改和滥用日志的新内容。

The program automatically gets new content in RecentChanges and Abuse logs of the Chinese Minecraft Wiki.

## 用途
当前功能与mcwzh-rc-monitor相同，剩余功能正在开发中。
<!--
每5秒尝试获取一次中文Minecraft Wiki最近更改的变化情况，新更改内容在Windows终端输出，如果是无巡查豁免权限的用户执行的操作还会产生通知弹窗并播放音效。

## 运作方式
在查询最近更改的链接后添加`&rcend=<时间戳>`可以获取自指定时间戳开始的所有内容。因此，程序每次获取内容都存储最新内容的时间戳和rcid，然后根据时间戳指定获取的数据，再根据rcid筛选出新内容，经过一系列处理后输出。

## 使用方法
程序需要同目录存在`config.json`才能正常运作。在这之前你应该需要先在[[Special:机器人密码]]创建一个机器人并获得密码，然后填入`config.json`。`Autopatrolled_user.json`不存在时只会在后台输出提示，然后所有用户均视为无巡查豁免权限。`sound.mp3`不存在时不会输出任何提示，只是照常运作程序，但不会播放音效。

使用前，请自行修改`config.json`中的用户代理。

## 注意事项
部分功能仅持有巡查员权限的用户可正常使用（其实只有特殊巡查那个链接才是）。程序仅在Windows 11上可用（其实只是我没在Windows 10上面测试过而已）。如果5秒内的最近更改新内容大于100条，程序只会处理最新的100条。
-->
## 授权协议
程序采用与Minecraft Wiki相同的CC BY-NC-SA 3.0协议授权。
