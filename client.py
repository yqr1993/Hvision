# -*- coding: utf-8 -*-

"""
just an tututorials about 
how to use the api.

the func all implements by
http post.
"""

import requests
import json
import base64


ip = "192.168.3.156"
port = "2021"


"""
@
@   some common function
@
"""


def http_post(post_url, post_data, post_files=None):
    res=requests.post(url=post_url, data=post_data, files=post_files)
    jsonData = json.loads(res.text)
    return jsonData


# calculate the match level
def compile_text(gt, ft, is_restrict=True):
    score = 0.0
    if is_restrict:
        if ft == gt:
            score = 1.0
        else:
            score = 0.0
    else:
        gt, ft = list(gt), list(ft)
        mcount = 0
        for t in ft:
            try:
                it = gt.index(t)
                gt[it] = ""
                # print(t + " is in " + str(it))
                mcount += 1
            except ValueError:
                # print(t + " is not in")
                pass
        score = mcount / len(gt)

    return score


"""
@
@   init url function
@
"""


# init the vision core
# camera usb id, if only one, then set 0
def init_the_visual_detection(camera_id=0):
    data = http_post("http://{}:{}/initCamera".format(ip, port), {"camera_id": camera_id})
    print(data)


# init the ocr core
# no param
def init_the_ocr():
    data = http_post("http://{}:{}/initOCR".format(ip, port), {})
    print(data)


"""
@
@   control uploadings and downloadings url function
@
"""


# upload the icon to the server and load in progress memory
# @param "icon_full_path" is the full path in master pc of the icon you prepare to upload, etc "/home/xxx/xxx/icon.png"
# @param "keyFn" is the icon filename , etc "icon.png"
# @param "scale" is the detection size range(+- scale / 2), correlated to instruction speed(the bigger, the slower)
# @param "Volume" is the max quentity of template that user uploads
# notice! only support jpg image file and png image file
def upload_icon(icon_full_path, keyFn, scale, Volume):
    data = http_post("http://{}:{}/loadIcon".format(ip, port), {"keyFn": keyFn, "scale": scale, "Volume": Volume}, post_files = {"iconFile": open(icon_full_path, "rb")})
    print(data)


# delete the icons that has been uploaded to the server in progress memory
def del_all_target():
    data = http_post("http://{}:{}/delAllTarget".format(ip, port), {})
    print(data)


# capture one current frame
# @param "save_full_path" is the full path to save the render image you want anywhere , etc "/home/xxx/xxx/icon.png"
# notice! only support jpg image file
def capture_one_current_frame(save_full_path):
    data = http_post("http://{}:{}/capture".format(ip, port), {})
    if data["image"]:
        with open(save_full_path,'wb') as f:
                f.write(base64.b64decode(data["image"]))
    else:
        print("no image")


"""
@
@   detecting task url function
@
"""


# find the target you just upload by call func of "upload_icon"
# @param "icon_name" is the icon filename, is the key of the icon you just uploadding , etc "icon.png"
# @param "OV" is the confidence threshold of icon detection
# @param "save_full_path" is the full path to save the render image you want anywhere , etc "/home/xxx/xxx/icon.png"
# @param "if_save_show_image" decide whether to save render image , 1 : i want , 0 : i dont want
# notice! only support jpg image file
def find_icon_in_frame(icon_name, OV, if_save_show_image, save_full_path=""):
    data = http_post("http://{}:{}/findIcon".format(ip, port), {"iconName": icon_name, "OV": OV, "saveShow": if_save_show_image})

    if if_save_show_image:
        if data["image"]:
            with open(save_full_path, 'wb') as f:
                    f.write(base64.b64decode(data["image"]))
        else:
            print("no image")

    print(data["detRet"])

    return data["detRet"]


# find text info in frame
# no param
def find_text():
    data = http_post("http://{}:{}/findText".format(ip, port), {})
    print(data)

    # find the text_box_position
    # text_box_position format : list : [["text1", cx, cy], ["text2", cx, cy], ["text3", cx, cy], ...], cx, cy is pixel index
    ret = []
    for d in data["ocrRet"]:
        ret.append(d)

    return ret


"""
@
@   measure task url function
@
"""


# measure the pixel point
# @param "pts" the points you want to measure
def measure_the_pixel_point(pts, fx=641.908787, cx=688.383484, fy=639.740430, cy=374.862427, Zc=245.0):
    ret = []
    for p in pts:
        rdr = http_post("http://{}:{}/measureXY".format(ip, port), {"x": p[0], "y": p[1], "fx": fx, "cx": cx, "fy": fy, "cy": cy, "Zc": Zc})
        ret.append(rdr["xyz"])
    print(ret)

    return ret


"""
@
@   complex task url function
@   maybe combinations of functions defined above
@
"""


# measure the device screen size you want, this will return more than one if there is not just one target
# @param "icon_name" the screen template you upload, so just one kind screen will be detected at the same time
# @param "OV" is the confidence threshold of icon detection
# @param "shape" you should define the shape of the screen by yourself
def get_device_size(icon_name, OV, shape):
    size_info_ret = []

    rect_data = find_icon_in_frame(icon_name, OV, 1, "capture_save.jpg")
    if not rect_data:
        return size_info_ret
    
    for pd in rect_data:
        size_info = {}
        if shape == "square":
            x1, y1, x2, y2 = pd[0], pd[1], pd[0] + pd[2], pd[1] + pd[3]
            m_ret = measure_the_pixel_point([[x1, y1], [x2, y2]])

            xx1, yy1 = m_ret[0]
            xx2, yy2 = m_ret[1]

            size_info['shape'] = "square"
            size_info['info'] = {"x": xx1, "y": yy1, "w": abs(xx2 - xx1), "h": abs(yy2 - yy1)}

            size_info_ret.append(size_info)

        elif shape == "circle":
            x1, y1, x2, y2 = pd[0], pd[1], pd[0] + pd[2], pd[1] + pd[3]
            m_ret = measure_the_pixel_point([[x1, y1], [x2, y2]])

            xx1, yy1 = m_ret[0]
            xx2, yy2 = m_ret[1]

            size_info['shape'] = "circle"
            size_info['info'] = {"x": (xx1 + xx2) / 2, "y": (yy1 + yy2) / 2, "radius": (abs(xx2 - xx1) + abs(yy2 - yy1)) / 4}

            size_info_ret.append(size_info)

    return size_info_ret


# measure the icons just detected by template
# @param "icon_name" the icon template you upload, so just one kind icon will be detected at the same time
# @param "OV" is the confidence threshold of icon detection
def find_icon_in_frame_and_measure_them(icon_name, OV):
    rect_data = find_icon_in_frame(icon_name, OV, 1, "capture_save.jpg")
    if not rect_data:
        return []

    pts_data = [[pp[0], pp[1]] for pp in rect_data]
    m_ret = measure_the_pixel_point(pts_data)

    return m_ret
