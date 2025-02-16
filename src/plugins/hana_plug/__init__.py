from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot import V11Event,V11Message, V11MessageSegment
from nonebot.params import CommandArg #参数

import os
import requests
from urllib.parse import unquote, urlparse
from nonebot import logger

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hana-plug",
    description="花花的插件，发色图+ai对话",
    usage="@机器人 发|来点|色图 [*n|tag|tag、tag|tag*n|tag、tag*n]",
    config=Config,
)

config = get_plugin_config(Config)

setu = on_command("发", rule=to_me(), aliases={"来点", "色图"}, priority=10, block=True)

@setu.handle()
async def handle_function(args: V11Message = CommandArg()):
    loliconurl = config.loliconurl
    loliconurl = parse_text(loliconurl,args.extract_plain_text())  #解析文本并拼接到url
    logger.opt(colors=True).warning(f"loliconurl:[{loliconurl}]")
    # 构建消息列表
    messages = []
    # 获取 JSON 数据
    data = fetch_json(loliconurl)
    logger.opt(colors=True).warning(f"data:[{data}]")
    if not data:
        await setu.finish(V11MessageSegment.text("失败了喵"))#发送图片消息
    for item in data["data"]:
        # 从 JSON 中提取图片信息
        pid = item["pid"]  # 作品 ID
        p = item["p"]  # 页码
        ext = item["ext"]  # 文件扩展名
        url = item["urls"][config.loliconurl_size]  # 图片 URL
      
        # 构建pid文本消息段
        pid_message = V11MessageSegment.text(f"pid: {pid}")
        # 从 URL 中提取文件名
        filename = extract_filename_from_url(url,pid)
        # 本地保存路径
        local_path = os.path.join(config.temp_img_path, filename)  # 保存到配置的文件夹

        # 确保配置的文件夹存在
        os.makedirs(config.temp_img_path, exist_ok=True)
        # 下载图片
        download_image(url, local_path)
        # 构建图片消息段
        image_message = V11MessageSegment.image(f"file:///{config.temp_img_path}/{filename}")
        # 添加到消息列表
        messages.extend([pid_message, image_message])
    # 发送消息
    await setu.finish(V11Message(messages))

def parse_text(url: str,text: str):
    """
    截取 *或 × 前后的字符串
    :param text: 输入的文本
    :return: 返回处理完成后的url
    """
    logger.opt(colors=True).warning(f"text:[{text}]")
    if text.__len__ == 0:
        return url
    num = ''
    tag = None
    # 找到 '*' 或 '×' 的位置
    star_index = text.find('*')
    cross_index = text.find('×')
    #按符号分割
    result = []
    if star_index != -1:
        result = text.split('*')
    elif cross_index != -1:
        result = text.split('×')
    #获取数量和tag
    if len(result) == 1:
        if result[0].isdigit():
            num = result[0].strip()
        else:
            tag = result[0].strip()
    elif len(result) == 2:
        num = result[1].strip()
        tag = result[0].strip()
    else:
        num = '1'
        tag = text.strip()
    url = f"{url}&num={num}"
    if len(tag) > 0:
        # 将 tag 按 、 分割成列表
        tags = tag.split("、") if tag else []
        for tag_s in tags:
            url = f"{url}&tag={tag_s}"
    return url
        
def fetch_json(url):
    """
    从指定的 URL 获取 JSON 数据
    :param url: 请求的 URL
    :return: 解析后的 JSON 数据
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回 JSON 数据
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    
def extract_filename_from_url(url,pid):
    """
    从 URL 中提取文件名
    :param url: 图片的 URL
    :return: 文件名（不包含路径）
    """
    # 解析 URL
    parsed_url = urlparse(url)
    # 获取路径部分并解码（处理特殊字符）
    path = unquote(parsed_url.path)
    # 提取文件名
    filename = os.path.basename(path)
    return filename if filename else f"{pid}.jpg"  # 如果无法提取文件名，使用默认名称

def download_image(url, save_path):
    """
    从指定的 URL 下载图片并保存到本地
    :param url: 图片的网络地址
    :param save_path: 图片保存的本地路径
    :return: 无
    """
    try:
        # 发送 HTTP GET 请求获取图片内容
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 将图片内容写入本地文件
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.exceptions.RequestException as e:
        print(f"下载图片失败: {e}")
