import json
import html

import requests
from datetime import datetime
import pytz


def get_beijing_time():
    """获取北京时间"""
    target_timezone = pytz.timezone('Asia/Shanghai')
    return datetime.now().astimezone(target_timezone)


def format_now():
    """格式化当前时间"""
    return get_beijing_time().strftime("%Y-%m-%d %H:%M:%S")


class PushConfig:
    """推送配置类"""

    def __init__(self,
                 push_plus_token=None,
                 push_plus_hour=None,
                 push_plus_max=30,
                 push_wechat_webhook_key=None,
                 telegram_bot_token=None,
                 telegram_chat_id=None):
        self.push_plus_token = push_plus_token
        self.push_plus_hour = push_plus_hour
        self.push_plus_max = int(push_plus_max) if push_plus_max else 30
        self.push_wechat_webhook_key = push_wechat_webhook_key
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id


def push_plus(token, title, content):
    """
    推送消息类型为html 需要在外部组装html代码的content
    :param token: PUSHPLUS 的token
    :param title: 推送标题
    :param content: 推送内容
    :return: none
    """
    requestUrl = f"http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "html",
        "channel": "wechat"
    }
    try:
        response = requests.post(requestUrl, data=data)
        if response.status_code == 200:
            json_res = response.json()
            print(f"pushplus推送完毕：{json_res['code']}-{json_res['msg']}")
        else:
            print("pushplus推送失败")
    except requests.exceptions.RequestException as e:
        print(f"pushplus推送网络异常: {e}")
    except Exception as e:
        print(f"pushplus推送未知异常: {e}")


def push_wechat_webhook(key, title, content):
    """
    推送企业微信通知，WebHook方式，需要注册企业微信并配置机器人到对应的推送群。然后提取对应的key

    :param key: WebHook机器人的key
    :param title: 推送标题
    :param content: 推送内容，虽然支持markdown，但是在使用微信插件时，消息不能被完整展示，直接使用纯文本效果会更好
    :return:
    """

    requestUrl = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"

    payload = {
        "msgtype": "markdown_v2",
        "markdown_v2": {
            "content": buildWeChatContent(title, content)
        }
    }

    try:
        response = requests.post(requestUrl, json=payload)
        if response.status_code == 200:
            json_res = response.json()
            if json_res.get('errcode') == 0:
                print(f"企业微信推送完毕：{json_res['errmsg']}")
            else:
                print(f"企业微信推送失败：{json_res.get('errmsg', '未知错误')}")
        else:
            print("企业微信推送失败")
    except requests.exceptions.RequestException as e:
        print(f"企业微信推送异常: {e}")
    except Exception as e:
        print(f"企业微信推送发生未知异常: {e}")


def buildWeChatContent(title, content) -> str:
    return f"""# {title}\n{content}"""


def html_escape(text):
    if text is None:
        return ''
    return html.escape(str(text), quote=False)


def build_html_summary(summary, exec_results, max_detail):
    content = f'<b>{html_escape(summary)}</b><br>'
    content += '━━━━━━━━━━━━━━<br>'
    if len(exec_results) >= max_detail:
        content += '<i>账号数量过多，详细情况请前往github actions中查看</i>'
        return content

    for exec_result in exec_results:
        user_display = html_escape(exec_result.get('user_display') or exec_result.get('user'))
        step = html_escape(exec_result.get('step') or '-')
        success_text = '成功' if exec_result.get('success') else '失败'
        status = success_text
        if exec_result.get('success') is not True:
            reason = exec_result.get('reason') or exec_result.get('msg') or '未知原因'
            status = f'{success_text} + {html_escape(reason)}'
        
        content += f'账号：{user_display}<br>'
        content += f'步数：{step}<br>'
        content += f'状态：{status}<br>'
        content += '━━━━━━━━━━━━━━<br>'
    return content


def build_text_summary(summary, exec_results, max_detail):
    content = f'{summary}\n━━━━━━━━━━━━━━'
    if len(exec_results) >= max_detail:
        content += '\n账号数量过多，详细情况请前往github actions中查看'
        return content

    for exec_result in exec_results:
        user_display = exec_result.get('user_display') or exec_result.get('user')
        step = exec_result.get('step') or '-'
        success_text = '成功' if exec_result.get('success') else '失败'
        status = success_text
        if exec_result.get('success') is not True:
            reason = exec_result.get('reason') or exec_result.get('msg') or '未知原因'
            status = f'{success_text} + {reason}'
        
        content += f'\n账号：{user_display}'
        content += f'\n步数：{step}'
        content += f'\n状态：{status}'
        content += '\n━━━━━━━━━━━━━━'
    return content


def build_telegram_summary(summary, exec_results, max_detail):
    content = f'<b>{html_escape(summary)}</b>\n'
    content += '━━━━━━━━━━━━━━\n'
    if len(exec_results) >= max_detail:
        content += '<i>账号数量过多，详细情况请前往github actions中查看</i>'
        return content

    for exec_result in exec_results:
        user_display = html_escape(exec_result.get('user_display') or exec_result.get('user'))
        step = html_escape(exec_result.get('step') or '-')
        success_text = '成功' if exec_result.get('success') else '失败'
        status = success_text
        if exec_result.get('success') is not True:
            reason = exec_result.get('reason') or exec_result.get('msg') or '未知原因'
            status = f'{success_text} + {html_escape(reason)}'
        
        content += f'账号：{user_display}\n'
        content += f'步数：{step}\n'
        content += f'状态：{status}\n'
        content += '━━━━━━━━━━━━━━\n'
    return content


def push_telegram_bot(bot_token, chat_id, content):
    """
    推送消息类型为html 需要在外部组装html content
    :param bot_token: telegram bot token
    :param chat_id: telegram bot chat_id
    :param content: 推送内容
    :return: none
    """
    requestUrl = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": int(chat_id),
        "text": content,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    print(f"post to url: {requestUrl}")
    print(f"payload: {json.dumps(payload)}")
    try:
        response = requests.post(requestUrl, json=payload)
        if response.status_code == 200:
            json_res = response.json()
            if json_res.get('ok') is True:
                print(f"telegram bot推送完毕：{json_res['result']['message_id']}")
            else:
                print(f"telegram bot推送失败: {json.dumps(json_res, ensure_ascii=False)}")
        else:
            text = response.text
            print(f"telegram bot推送失败: {response.status_code} {text}")
    except requests.exceptions.RequestException as e:
        print(f"telegram bot推送异常: {e}")
    except Exception as e:
        print(f"telegram bot推送发生未知异常: {e}")


def push_results(exec_results, summary, config: PushConfig):
    """推送所有结果"""
    if not_in_push_time_range(config):
        return
    push_to_push_plus(exec_results, summary, config)
    push_to_wechat_webhook(exec_results, summary, config)
    push_to_telegram_bot(exec_results, summary, config)


def not_in_push_time_range(config: PushConfig) -> bool:
    """检查是否在推送时间范围内"""
    if not config.push_plus_hour:
        return False  # 如果没有设置推送时间，则总是推送

    time_bj = get_beijing_time()

    # 首先根据时间判断，如果匹配 直接返回
    if config.push_plus_hour.isdigit():
        if time_bj.hour == int(config.push_plus_hour):
            print(f"当前设置推送整点为：{config.push_plus_hour}, 当前整点为：{time_bj.hour}，执行推送")
            return False

    # 如果时间不匹配，检查cron_change_time文件中的记录
    # 读取cron_change_time文件中的最后一行数据：“next exec time: UTC(7:35) 北京时间(15:35)” 中的整点数
    # 然后用来对比是否当前时间，避免因为Actions执行延迟导致推送失效
    try:
        with open('cron_change_time', 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                # 提取北京时间的小时数
                import re
                match = re.search(r'北京时间\(0?(\d+):\d+\)', last_line)
                if match:
                    cron_hour = int(match.group(1))
                    if int(config.push_plus_hour) == cron_hour:
                        print(
                            f"当前设置推送整点为：{config.push_plus_hour}, 根据执行记录，本次执行整点为：{cron_hour}，执行推送")
                        return False
    except Exception as e:
        print(f"读取cron_change_time文件出错: {e}")
    print(f"当前整点时间为：{time_bj}，不在配置的推送时间，不执行推送")
    return True


def push_to_push_plus(exec_results, summary, config: PushConfig):
    """推送到PushPlus"""
    # 判断是否需要pushplus推送
    if config.push_plus_token and config.push_plus_token != '' and config.push_plus_token != 'NO':
        html = build_html_summary(summary, exec_results, config.push_plus_max)
        push_plus(config.push_plus_token, f"{format_now()} 刷步数通知", html)
    else:
        print("未配置 PUSH_PLUS_TOKEN 跳过PUSHPLUS推送")


def push_to_wechat_webhook(exec_results, summary, config: PushConfig):
    """推送到企业微信"""
    # 判断是否需要微信推送
    if config.push_wechat_webhook_key and config.push_wechat_webhook_key != '' and config.push_wechat_webhook_key != 'NO':

        content = f'{summary}\n━━━━━━━━━━━━━━'
        if len(exec_results) >= config.push_plus_max:
            content += '\n账号数量过多，详细情况请前往github actions中查看'
        else:
            for exec_result in exec_results:
                user_display = exec_result.get('user_display') or exec_result.get('user')
                step = exec_result.get('step') or '-'
                success_text = '成功' if exec_result.get('success') else '失败'
                status = success_text
                if exec_result.get('success') is not True:
                    reason = exec_result.get('reason') or exec_result.get('msg') or '未知原因'
                    status = f'{success_text} + {reason}'
                content += f'\n账号：{user_display}'
                content += f'\n步数：{step}'
                content += f'\n状态：{status}'
                content += '\n━━━━━━━━━━━━━━'
        push_wechat_webhook(config.push_wechat_webhook_key, f"{format_now()} 刷步数通知", content)
    else:
        print("未配置 WECHAT_WEBHOOK_KEY 跳过微信推送")


def push_to_telegram_bot(exec_results, summary, config: PushConfig):
    """推送到Telegram"""
    # 判断是否需要telegram推送
    if (config.telegram_bot_token and config.telegram_bot_token != '' and config.telegram_bot_token != 'NO' and
            config.telegram_chat_id and config.telegram_chat_id != ''):
        content = build_telegram_summary(summary, exec_results, config.push_plus_max)
        push_telegram_bot(config.telegram_bot_token, config.telegram_chat_id, content)
    else:
        print("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 跳过telegram推送")
