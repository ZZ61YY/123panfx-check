import os
import requests
import json

def mask_string(s: str, visible_prefix_len=8, visible_suffix_len=8):
    """对敏感字符串进行遮挡处理，只显示头尾部分"""
    if not s or len(s) <= visible_prefix_len + visible_suffix_len:
        return s
    return f"{s[:visible_prefix_len]}...{s[-visible_suffix_len:]}"

def check_in():
    """
    执行签到并提供详细调试信息
    """
    # --- 1. 获取环境变量 ---
    cookie = os.environ.get('PAN_COOKIE')
    # 检查环境变量 DEBUG_MODE 是否为 'true'，从而决定是否开启调试模式
    is_debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'

    if not cookie:
        print("❌ 错误：未找到名为 PAN_COOKIE 的环境变量。")
        print("请在 GitHub Secrets 中设置你的 Cookie。")
        return

    if is_debug_mode:
        print("--- 调试模式已开启 ---")
        print(f"读取到的 PAN_COOKIE (已做遮挡处理): {mask_string(cookie)}")
        print("------------------------\n")

    # --- 2. 配置请求参数 ---
    url = "https://pan1.me/?my-sign.htm"
    headers = {
        'Accept': 'text/plain, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Host': 'pan1.me',
        'Origin': 'https://pan1.me',
        'Referer': 'https://pan1.me/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36 EdgA/137.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
    }

    if is_debug_mode:
        print("--- 准备发送的请求详情 ---")
        print(f"URL: {url}")
        print("Method: POST")
        print("Headers:")
        for key, value in headers.items():
            # 再次对 Cookie 进行遮挡处理
            if key.lower() == 'cookie':
                print(f"  {key}: {mask_string(value)}")
            else:
                print(f"  {key}: {value}")
        print("Body: (空)")
        print("--------------------------\n")

    # --- 3. 发送请求并处理响应 ---
    try:
        print("🚀 正在发送签到请求...")
        response = requests.post(url, headers=headers, timeout=20)

        if is_debug_mode:
            print("--- 收到服务器响应 ---")
            print(f"状态码 (Status Code): {response.status_code}")
            print("\n响应头 (Response Headers):")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            print("\n响应体原文 (Raw Response Body):")
            # 直接打印原始文本，因为如果出错可能不是 JSON 格式
            print(response.text)
            print("------------------------\n")

        # 检查 HTTP 状态码是否表示成功
        response.raise_for_status()

        # 尝试解析 JSON
        try:
            result = response.json()
            if result.get('code') == '0':
                message = result.get('message', '签到成功，但未获取到具体信息。')
                print(f"✅ 签到成功！服务器返回信息：{message}")
            else:
                message = result.get('message', '未知错误')
                print(f"❌ 签到失败。服务器返回信息：{message}")
                print("请检查上方 '响应体原文' 以分析失败原因。")
        except json.JSONDecodeError:
            print("❌ 签到失败：服务器响应不是有效的 JSON 格式。")
            print("这通常意味着你的 Cookie 已失效或请求被拦截。请检查上方 '响应体原文'，可能是一个 HTML 登录页面。")

    except requests.exceptions.HTTPError as e:
        print(f"❌ 请求失败：HTTP 错误。状态码: {e.response.status_code}")
        print("常见原因：401/403 (Cookie 失效或无权限)，5xx (服务器内部错误)。")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 请求失败：网络连接错误。无法连接到服务器。")
    except requests.exceptions.Timeout:
        print(f"❌ 请求失败：请求超时。服务器在规定时间内未响应。")
    except requests.exceptions.RequestException as e:
        print(f"❌ 发生未知请求错误: {e}")


if __name__ == "__main__":
    check_in()
