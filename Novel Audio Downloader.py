# **************************************************
# 免责声明：
# 本代码仅供学习和研究使用，严禁用于任何商业用途。
# 作者不对使用本代码导致的任何后果负责。
# 在使用本代码时，请遵守相关法律法规和网站的使用规定。
# **************************************************

import os
import tkinter as tk
from tkinter import simpledialog
import requests
import re
import json

# ANSI转义码
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'

def clean_filename(filename):
    # 移除非法字符
    return re.sub(r'[\/:*?"<>|]', '', filename)

def download_novel(id, page_num):
    current_page_file = "pageid_.txt"

    # 提示用户输入当前页数
    current_page = simpledialog.askinteger("输入", "请输入从第几页开始下载:")

    if current_page is None:
        print(Colors.RED + "未输入当前页数，退出下载" + Colors.ENDC)
        return

    if current_page > page_num:
        print(Colors.GREEN + "全部下载完成" + Colors.ENDC)
        return

    base_url = "https://www.ysts.cc/tingshu"
    session = requests.Session()

    url = "{}/{}/?p={}".format(base_url, id, current_page)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,zh-TW;q=0.4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://www.ysts.cc',
        'Referer': '{}/{}/41440.html'.format(base_url, id),
    }

    try:
        response = download_file(session, url, headers)
        a_rule = fr'<a href="/tingshu/{id}/(\d+)\.html" target="_blank" title="([^"]+)">'
        match_a = re.findall(a_rule, response.text, re.S)

        if not match_a:
            print(Colors.RED + "未获取到数据，请检查输入参数是否正确！" + Colors.ENDC)
            return

        # 创建整个音频的保存路径
        folder_path = os.path.join("Novel audio")
        os.makedirs(folder_path, exist_ok=True)

        for match in match_a:
            mid = match[0]
            name = match[1]
            name_cleaned = clean_filename(name)
            url = "{}/{}/{}.html".format(base_url, id, mid)
            response = download_file(session, url, headers)
            c_rule = r'<meta name="_c" content="([^"]+)" />'
            match_b = re.findall(c_rule, response.text, re.S)

            if not match_b:
                print(Colors.RED + "未获取SC" + Colors.ENDC)
                return

            sc = match_b[0]
            play_url = "https://www.ysts.cc/api/act/play"
            headers_play = headers.copy()
            headers_play["sc"] = sc
            print(f"{name}...")

            params_play = {'nid': id, 'cid': mid}
            response_play = session.post(play_url, headers=headers_play, data=params_play, timeout=60)
            response_play.raise_for_status()

            # Check if the response is JSON
            if 'application/json' in response_play.headers['content-type']:
                try:
                    result_play = response_play.json()
                except json.JSONDecodeError:
                    print(Colors.RED + "未能正确解析JSON响应" + Colors.ENDC)
                    return
            else:
                print(Colors.RED + "未获取正确的播放数据" + Colors.ENDC)
                return

            novel_title_rule = r'<title>(.*?)</title>'
            novel_title_match = re.search(novel_title_rule, response.text)

            if novel_title_match:
                novel_title = clean_filename(novel_title_match.group(1).strip())
            else:
                print(Colors.RED + "未获取小说标题" + Colors.ENDC)
                return

            # 检查文件是否已存在
            audio_file_path = os.path.join(folder_path, f"{name_cleaned}.m4a")
            if os.path.exists(audio_file_path):
                print(Colors.YELLOW + f"此音频文件已存在，跳过下载！" + Colors.ENDC)
            else:
                # 保存音频文件
                with open(audio_file_path, "wb") as file:
                    file.write(download_file(session, result_play['url'], headers_play, timeout=60).content)
                print(Colors.GREEN + "此音频下载完成!\n" + Colors.ENDC)

        # 将 "全部下载完成" 移到循环外部
        print(Colors.GREEN + "全部下载完成" + Colors.ENDC)

        # 将当前页数写入文件
        with open(current_page_file, "w") as file:
            file.write(str(current_page))
    except KeyboardInterrupt:
        print(Colors.YELLOW + "下载已被用户中断！" + Colors.ENDC)
    except Exception as e:
        print(Colors.RED + f'下载失败：{str(e)}' + Colors.ENDC)

def download_file(session, url, headers, params=None, method='GET', timeout=30):
    response = session.request(method, url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    return response

def main():
    root = tk.Tk()
    root.withdraw()  # 不显示 tkinter 窗口

    try:
        album_id = simpledialog.askinteger("输入", "请输入专辑ID:")
        page_num = simpledialog.askinteger("输入", "请输入总下载页数:")
        download_novel(album_id, page_num)
    except KeyboardInterrupt:
        print(Colors.YELLOW + "下载已被用户中断！" + Colors.ENDC)
    except Exception as e:
        print(Colors.RED + f'下载失败：{str(e)}' + Colors.ENDC)

if __name__ == "__main__":
    main()
