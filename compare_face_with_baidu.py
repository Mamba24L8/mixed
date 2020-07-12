# -*- coding: utf-8 -*-
"""
Created on 2020/7/10 10:58

@Author: Mamba

@Purpose: 百度人脸识别接口

@ModifyRecord:
"""
import base64
import hashlib
import json
import requests
import time

from glob import glob, iglob
from pathlib import Path
from urllib.parse import urlencode


def get_base64_image(image_file):
    """ base64编码的图片"""
    with open(image_file, "rb") as f:
        base64_data = base64.b64encode(f.read())
        return base64_data.decode()


def get_access_token():
    base_url = "https://aip.baidubce.com/oauth/2.0/token?"
    params = {
        "grant_type": "client_credentials",
        "client_id": "6lIGcGMLbTQpdrvcM1LsRsTN",
        "client_secret": "XTqmf9OG3GT0HI0Y8xTX6YhTIlvSe50G"
    }
    url = base_url + urlencode(params)
    response = requests.get(url)
    if response:
        response = response.json()
        return response["access_token"]


def generate_params_compare(image):
    """

    Parameters
    ----------
    image : str, 图片文件名，或者base64后的图片

    References
    ----------
    https://cloud.baidu.com/doc/FACE/s/Gk37c1uzc

    Returns
    -------
    dict
    """
    if Path(image).is_file():
        image = get_base64_image(image)
    return {
        "image": image,
        "image_type": "BASE64",
        "face_type": "LIVE",
        "quality_control": "NONE",  # 质量控制
        "liveness_control": "NONE"
    }


def generate_params_search(image, group_id_list, max_user_num=1):
    """

    Parameters
    ----------
    image : str, 图片路径或者base64编码后的图片
    group_id_list : 搜索的图片库
    max_user_num : 查找后返回的用户数量。返回相似度最高的几个用户，默认为1，最多返回50个

    Returns
    -------

    """
    params = generate_params_compare(image)
    params.update({"group_id_list": group_id_list, "max_user_num": max_user_num})
    return params


def generate_params_set(image, group_id, user_id, action_type="APPEND"):
    if Path(image).is_file():
        image = get_base64_image(image)
    return {
        "image": image,
        "image_type": "BASE64",
        "group_id": group_id,
        "user_id": user_id,
        "user_info": "",
        "quality_control": "NONE",
        "liveness_control": "NONE",
        "action_type": action_type
    }


def create_face_set(image, group_id, user_id, action_type="APPEND"):
    access_token = get_access_token()
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    params = generate_params_set(image, group_id, user_id, action_type=action_type)
    response = requests.post(request_url, data=json.dumps(params), headers=headers)
    if response:
        return response.json()


def create_group(group_id="target_person"):
    path_pattern = r"D:\Dataset\DataSet\pic\*\*.jpg"
    images = glob(path_pattern)
    for image in iglob(path_pattern):
        person_name = Path(image).parent.name
        user_id = hashlib.md5(person_name.encode("utf8")).hexdigest()
        response = create_face_set(image, group_id, user_id, action_type="APPEND")
        print(image)
        print(response)
        time.sleep(0.5)


def compare_face(image1, image2):
    """ 百度人脸对比接口"""
    access_token = get_access_token()
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/match"
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    params = list(map(generate_params_compare, [image1, image2]))
    response = requests.post(request_url, data=json.dumps(params), headers=headers)
    return response


def search_face(image, group_id_list="target_person", max_user_num=10):
    """

    Parameters
    ----------
    image
    group_id_list
    max_user_num

    Returns
    -------

    """
    access_token = get_access_token()
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    params = generate_params_search(image, group_id_list, max_user_num)
    response = requests.post(request_url, data=json.dumps(params), headers=headers)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise requests.RequestException("请求失败")


def face_set():
    pass


if __name__ == '__main__':
    image = r"D:\Dataset\DataSet\one_day\艾宝俊\0000102.jpg"
    a = search_face(image)
    print(a)
    # dirname = r"D:\Dataset\DataSet\100_1\*.jpg"
    # _image1, _image2 = r"D:\Dataset\DataSet\100_1\0_0.jpg", r"D:\Dataset\DataSet\100_1\2_1_1.jpg"
    # a = compare_face(_image1, _image2)
    # print(a.json())
