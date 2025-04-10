###############################################################################
#  Copyright (C) 2024 LiveTalking@lipku https://github.com/lipku/LiveTalking
#  email: lipku@foxmail.com
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
import multiprocessing
import traceback
from urllib.parse import urljoin
import uuid
import gc
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_sockets import Sockets
import base64
import time
import json
# import gevent
# from gevent import pywsgi
# from geventwebsocket.handler import WebSocketHandler
import os
import re
import numpy as np
from threading import Thread, Event
# import multiprocessing
import torch.multiprocessing as mp
from functools import partial
from aiohttp import web
import aiohttp
import aiohttp_cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.rtcrtpsender import RTCRtpSender
from webrtc import HumanPlayer
from rtcrecv import RtcRecv

import argparse
import random
from wsmanager import WebSocketManager
import shutil
import asyncio
from funcUtil import prewav2lip as mkprewav2lip, check_avatar
from logger import logger


app = Flask(__name__)
#####websocket############################
ws_manager = WebSocketManager()
nerfreals = {}
pre_nerfreals = {}
opt = None
model = None
avatar = None


# 需要实现SSE连接管理器（类似WebSocketManager）
class SSEManager:
    def __init__(self):
        self.connections = {}

    async def register(self, session_id, resp):
        self.connections[session_id] = resp

    async def unregister(self, session_id):
        if session_id in self.connections:
            # await self.connections[session_id].close()
            del self.connections[session_id]


sse_manager = SSEManager()
async def sse_handler(request):
    # 创建SSE响应对象
    resp = web.StreamResponse()
    resp.headers['Content-Type'] = 'text/event-stream'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Connection'] = 'keep-alive'
    await resp.prepare(request)

    session_id = uuid.uuid4().hex
    avatar_id = request.query.get('avatar', '')
    voice = request.query.get('voice', '')

    # 参数校验逻辑保持不变
    if not avatar_id:
        await send_sse_message(resp, json.dumps({
            'status': 1,
            'data': "请输入正确 avatar"
        }))
        await resp.write_eof()  # 使用 write_eof 结束响应
        return resp
    elif not check_avatar(avatar_id):
        await send_sse_message(resp, json.dumps({
            'status': 1,
            'data': "当前avatar_id不存在"
        }))
        await resp.write_eof()  # 使用 write_eof 结束响应
        return resp

    # 初始化逻辑保持不变（省略部分代码）
    avatar = avatar_id
    logger.info(f"avatar={avatar}")
    push_url = f"http://146.56.226.252:1985/rtc/v1/whip/?app=live&stream={session_id}"
    # 注册SSE连接（需自定义连接管理器）
    await sse_manager.register(session_id, resp)
    await send_sse_message(resp, json.dumps({
        'status': 0,
        'sessionid': session_id,
        'data': f"/rtc/v1/whep/?app=live&stream={session_id}"
    }, ensure_ascii=False))
    try:
        # 创建数字人实例逻辑保持不变（部分代码省略）
        build_nerfreal_with_params = partial(_build_nerfreal, avatar_id, voice)
        nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal_with_params, session_id)
        nerfreal.ws_uri = opt.ws_uri
        # while not nerfreal.start_event.is_set():
        #     await asyncio.sleep(0.1)

        # 建立WebRTC连接逻辑保持不变（需适配SSE）
        pc = await _run(push_url, nerfreal)
        await send_sse_message(resp, json.dumps({
            'status': 0,
            'sessionid': session_id,
            'data': f"/rtc/v1/whep/?app=live&stream={session_id}"
        }, ensure_ascii=False))
        # 消息循环逻辑转换为SSE格式
        while not nerfreal.stop_event.is_set():
            msg = await nerfreal.msg_queue.get()
            await send_sse_message(resp, msg)
            await asyncio.sleep(0.1)
            if resp._eof_sent:  # 使用 _eof_sent 检查连接状态
                break
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
    finally:
        try:
            await sse_manager.unregister(session_id)
            await pc.close()
            await resp.write_eof()  # 使用 write_eof 结束响应
        except:
            ...
        gc.collect()

    return resp


async def send_sse_message(resp, data):
    message = f"data: {data}\n\n"
    try:
        await resp.write(message.encode('utf-8'))
    except ConnectionResetError:
        await resp.write_eof()  # 使用 write_eof 结束响应


async def websocket_handler(request):
    # 创建 WebSocket 响应对象
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    session_id = uuid.uuid4().hex
    avatar_id = request.query.get('avatar', '')
    voice = request.query.get('voice', '')
    if not avatar_id:
        await ws.send_str(json.dumps({
            'status': 1,
            'data': "请输入正确 avatar"
        }, ensure_ascii=False))
        await ws.close()
        return
    elif not check_avatar(avatar_id):
        await ws.send_str(json.dumps({
            'status': 1,
            'data': "当前avatar_id不存在"
        }, ensure_ascii=False))
        await ws.close()
        return
    avatar = avatar_id
    logger.info(f"avatar={avatar}")
    push_url = f"http://146.56.226.252:1985/rtc/v1/whip/?app=live&stream={session_id}"
    await ws.send_str(json.dumps({
        'status': 0,
        'sessionid': session_id,
        'data': f"/rtc/v1/whep/?app=live&stream={session_id}"
    }, ensure_ascii=False))
    try:
        # 注册 WebSocket 连接
        await ws_manager.register(session_id, ws)
        # 创建数字人实例
        build_nerfreal_with_params = partial(_build_nerfreal, avatar_id, voice)
        nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal_with_params, session_id)
        nerfreal.ws_uri = opt.ws_uri
        # 建立流程
        pc = await _run(push_url,nerfreal)
        # 处理 WebSocket 消息
        while not nerfreal.stop_event.is_set():
            await ws.send_str(await nerfreal.msg_queue.get())
            await asyncio.sleep(0.1)
            if ws.closed:
                break
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(error_stack)
        # 取消注册 WebSocket 连接
    finally:
        try:
            await ws_manager.unregister(session_id)
            await pc.close()
        except:
            ...
        gc.collect()
async def create_preloader(request):
    print(":::api:::create_preloader:::")
    params = await request.json()
    avatar_id = params.get('avatar_id', "")
    if avatar_id in pre_nerfreals:
        msg = "实例已存在"
        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"msg": msg}
            )
        )
    try:

        if opt.model == 'wav2lip':
            from lipreal import load_avatar
            avatar = load_avatar(avatar_id)
        # elif opt.model == 'wav2lipls':
        #     from liplsreal import load_model,load_avatar,warm_up
        #     print(opt)
        #     model = load_model("./models/checkpoint_step000562000.pth")
        # avatar = load_avatar(opt.avatar_id)
        #     nerfreal = MuseReal(opt,model,avatar)
        # elif opt.model == 'ernerf':
        #     from nerfreal import NeRFReal
        #     nerfreal = NeRFReal(opt,model,avatar)
        pre_nerfreals[avatar_id] = avatar
        msg = "ok"
    except:
        traceback.print_exc()
        msg = "error"
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"msg": msg}
        )
    )


async def delete_preloader(request):
    print(":::api:::delete_preloader:::")
    params = await request.json()
    avatar_id = params.get('avatar_id', "")
    try:
        del pre_nerfreals[avatar_id]
        msg = "ok"
    except:
        msg = "实例不存在"
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"msg": msg}
        )
    )


def llm_response(message, nerfreal):
    start = time.perf_counter()
    from openai import OpenAI
    client = OpenAI(
        # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        # 填写DashScope SDK的base_url
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    end = time.perf_counter()
    print(f"llm Time init: {end - start}s")
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                  {'role': 'user', 'content': message}],
        stream=True,
        # 通过以下设置，在流式输出的最后一行展示token使用信息
        stream_options={"include_usage": True}
    )
    result = ""
    first = True
    for chunk in completion:
        if len(chunk.choices) > 0:
            # print(chunk.choices[0].delta.content)
            if first:
                end = time.perf_counter()
                print(f"llm Time to first chunk: {end - start}s")
                first = False
            msg = chunk.choices[0].delta.content
            lastpos = 0
            # msglist = re.split('[,.!;:，。！?]',msg)
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；":
                    result = result + msg[lastpos:i + 1]
                    lastpos = i + 1
                    if len(result) > 10:
                        print(result)
                        nerfreal.put_msg_txt(result)
                        result = ""
            result = result + msg[lastpos:]
    end = time.perf_counter()
    print(f"llm Time to last chunk: {end - start}s")
    nerfreal.put_msg_txt(result)


#####webrtc###############################
pcs = set()


def randN(N):
    '''生成长度为 N的随机数 '''
    min = pow(10, N - 1)
    max = pow(10, N)
    return random.randint(min, max - 1)


def build_nerfreal(sessionid):
    opt.sessionid = sessionid
    if opt.model == 'wav2lip':
        from lipreal import LipReal
        nerfreal = LipReal(opt, model, avatar)
    elif opt.model == 'musetalk':
        from musereal import MuseReal
        nerfreal = MuseReal(opt, model, avatar)
    elif opt.model == 'ernerf':
        from nerfreal import NeRFReal
        nerfreal = NeRFReal(opt, model, avatar)
    return nerfreal


def _build_nerfreal(avatar_id, voice, sessionid):
    opt.sessionid = sessionid
    opt.voice = voice
    pre_nerfreal = pre_nerfreals.get(avatar_id)
    if pre_nerfreal:
        avatar = pre_nerfreal
    else:
        avatar = load_avatar(avatar_id)
    if opt.model == 'wav2lip':
        from lipreal import LipReal
        nerfreal = LipReal(opt, model, avatar)
    elif opt.model == 'wav2lipls':
        from liplsreal import LipLsReal
        nerfreal = LipLsReal(opt, model, avatar)
    elif opt.model == 'musetalk':
        from musereal import MuseReal
        nerfreal = MuseReal(opt, model, avatar)
    elif opt.model == 'ernerf':
        from nerfreal import NeRFReal
        nerfreal = NeRFReal(opt, model, avatar)
    return nerfreal


# @app.route('/offer', methods=['POST'])
async def offer(request):
    print(":::api:::offer:::")
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    # main_playfile = params.get('playfile','data/audio.wav')
    main_playfile = params.get('playfile', '')
    avatar_id = params.get('avatar', '')
    voice = params.get('voice', '')
    username = params.get('username', 'zhangsan')
    if len(nerfreals) >= opt.max_session:
        print('reach max session')
        return -1
    sessionid = randN(6)  # len(nerfreals)
    print('sessionid=', sessionid)
    nerfreals[sessionid] = None
    build_nerfreal_with_params = partial(_build_nerfreal, avatar_id, voice)
    nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal_with_params, sessionid)
    nerfreal.set_main_play(main_playfile)
    nerfreal.username = username
    nerfreal.ws_uri = opt.ws_uri
    nerfreal.set_datachannel(asyncio.Queue(), asyncio.get_event_loop())
    nerfreals[sessionid] = nerfreal
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
            del nerfreals[sessionid]
        if pc.connectionState == "closed":
            pcs.discard(pc)
            del nerfreals[sessionid]

    # 接收音频
    audiorecv = RtcRecv(nerfreals[sessionid])

    @pc.on("track")
    def on_track(track):
        print(f"Track %s received", track.kind)
        if track.kind == "audio":
            audiorecv.addTrack(track)

        @track.on("ended")
        async def on_ended():
            print(f"Track %s ended", track.kind)
            await audiorecv.stop()

    # datachannel
    async def send_msg(channel, dcqueue):
        while True:
            msg = await dcqueue.get()
            msg_json = json.loads(msg)
            content_length = len(msg_json.get('content', ''))
            if content_length == 0:
                continue
            print("send_msg:::", msg)
            channel.send(msg)
        print('dc sendmsg finish')

    @pc.on("datachannel")
    def on_datachannel(channel):
        task = asyncio.ensure_future(send_msg(channel, nerfreal.dcqueue))

        # asyncio.ensure_future(self.__run_track(track, context))
        @channel.on("close")
        def on_close():
            print('datachannel close')
            task.cancel()

        @channel.on("message")
        def on_message(message):
            # print("ping ping ping ping ping ping ping ping ping ping ping")
            print(message)
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    player = HumanPlayer(nerfreals[sessionid])
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)
    #####pref h264######################################
    capabilities = RTCRtpSender.getCapabilities("video")
    preferences = list(filter(lambda x: x.name == "H264", capabilities.codecs))
    preferences += list(filter(lambda x: x.name == "VP8", capabilities.codecs))
    preferences += list(filter(lambda x: x.name == "rtx", capabilities.codecs))
    transceiver = pc.getTransceivers()[1]
    transceiver.setCodecPreferences(preferences)
    ####################################################

    await pc.setRemoteDescription(offer)
    await audiorecv.start()

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # return jsonify({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    # await connect_to_websocket(opt.ws_uri, nerfreal)
    # asyncio.create_task(connect_to_websocket(opt.ws_uri, nerfreal))
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type, "sessionid": sessionid}
        ),
    )


async def human(request):
    params = await request.json()

    sessionid = params.get('sessionid', 0)
    if params.get('interrupt'):
        nerfreals[sessionid].flush_talk()

    if params['type'] == 'echo':
        nerfreals[sessionid].put_msg_txt(params['text'])
    elif params['type'] == 'chat':
        res = await asyncio.get_event_loop().run_in_executor(None, llm_response, params['text'], nerfreals[sessionid])
        # nerfreals[sessionid].put_msg_txt(res)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": "ok"}
        ),
    )


async def switch_radio(request):
    params = await request.json()
    sessionid = int(params.get('sessionid', 0))
    nerfreal = nerfreals[sessionid]
    action = params.get('action', 0)
    if action == "stop_radio":
        nerfreal.stop_radio = True
    elif action == "start_radio":
        nerfreal.stop_radio = False
    else:
        ...
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": "ok"}
        ),
    )


async def prewav2lip(request):
    print(":::api:::prewav2lip:::")
    data = await request.post()
    video_file = data['file']
    newAvatar = data["avatarName"]
    position = video_file.filename.index('.')
    suffix = video_file.filename[position:]
    preVideoName = newAvatar + suffix
    print("preVideoName:::", preVideoName)
    with open(os.path.join("wav2lip", preVideoName), "wb") as f:
        f.write(video_file.file.read())
    # asyncio.create_task(mkprewav2lip(data))
    _data = {
        "avatarName": newAvatar,
        "callbackUrl": data["callbackUrl"],
        'type': data['type'],
        'preVideoName':preVideoName
    }
    process = multiprocessing.Process(target=mkprewav2lip, args=(_data,))
    logger.info("训练子进程执行。。。")
    process.start()
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": "ok"}
        ),
    )


async def humanaudio(request):
    try:
        form = await request.post()
        sessionid = int(form.get('sessionid', 0))
        fileobj = form["file"]
        filename = fileobj.filename
        filebytes = fileobj.file.read()
        nerfreals[sessionid].put_audio_file(filebytes)

        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"code": 0, "msg": "ok"}
            ),
        )
    except Exception as e:
        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"code": -1, "msg": "err", "data": "" + e.args[0] + ""}
            ),
        )


async def set_audiotype(request):
    params = await request.json()

    sessionid = params.get('sessionid', 0)
    nerfreals[sessionid].set_curr_state(params['audiotype'], params['reinit'])

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": "ok"}
        ),
    )


async def record(request):
    params = await request.json()

    sessionid = params.get('sessionid', 0)
    if params['type'] == 'start_record':
        # nerfreals[sessionid].put_msg_txt(params['text'])
        nerfreals[sessionid].start_recording()
    elif params['type'] == 'end_record':
        nerfreals[sessionid].stop_recording()
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": "ok"}
        ),
    )


async def is_speaking(request):
    params = await request.json()

    sessionid = params.get('sessionid', 0)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": nerfreals[sessionid].is_speaking()}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


async def post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print(f'Error: {e}')
async def _run(push_url,nerfreal):
    # nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal,sessionid)
    # nerfreals[sessionid] = nerfreal

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    player = HumanPlayer(nerfreal)
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())
    answer = await post(push_url,pc.localDescription.sdp)
    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer,type='answer'))
    return pc

async def run(push_url, sessionid):
    nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal, sessionid)
    nerfreals[sessionid] = nerfreal

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    player = HumanPlayer(nerfreals[sessionid])
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())
    answer = await post(push_url, pc.localDescription.sdp)
    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer, type='answer'))


##########################################
# os.environ['MKL_SERVICE_FORCE_INTEL'] = '1'
# os.environ['MULTIPROCESSING_METHOD'] = 'forkserver'
if __name__ == '__main__':
    mp.set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('--pose', type=str, default="data/data_kf.json", help="transforms.json, pose source")
    parser.add_argument('--au', type=str, default="data/au.csv", help="eye blink area")
    parser.add_argument('--torso_imgs', type=str, default="", help="torso images path")

    parser.add_argument('-O', action='store_true', help="equals --fp16 --cuda_ray --exp_eye")

    parser.add_argument('--data_range', type=int, nargs='*', default=[0, -1], help="data range to use")
    parser.add_argument('--workspace', type=str, default='data/video')
    parser.add_argument('--seed', type=int, default=0)

    ### training options
    parser.add_argument('--ckpt', type=str, default='data/pretrained/ngp_kf.pth')

    parser.add_argument('--num_rays', type=int, default=4096 * 16,
                        help="num rays sampled per image for each training step")
    parser.add_argument('--cuda_ray', action='store_true', help="use CUDA raymarching instead of pytorch")
    parser.add_argument('--max_steps', type=int, default=16,
                        help="max num steps sampled per ray (only valid when using --cuda_ray)")
    parser.add_argument('--num_steps', type=int, default=16,
                        help="num steps sampled per ray (only valid when NOT using --cuda_ray)")
    parser.add_argument('--upsample_steps', type=int, default=0,
                        help="num steps up-sampled per ray (only valid when NOT using --cuda_ray)")
    parser.add_argument('--update_extra_interval', type=int, default=16,
                        help="iter interval to update extra status (only valid when using --cuda_ray)")
    parser.add_argument('--max_ray_batch', type=int, default=4096,
                        help="batch size of rays at inference to avoid OOM (only valid when NOT using --cuda_ray)")

    ### loss set
    parser.add_argument('--warmup_step', type=int, default=10000, help="warm up steps")
    parser.add_argument('--amb_aud_loss', type=int, default=1, help="use ambient aud loss")
    parser.add_argument('--amb_eye_loss', type=int, default=1, help="use ambient eye loss")
    parser.add_argument('--unc_loss', type=int, default=1, help="use uncertainty loss")
    parser.add_argument('--lambda_amb', type=float, default=1e-4, help="lambda for ambient loss")

    ### network backbone options
    parser.add_argument('--fp16', action='store_true', help="use amp mixed precision training")

    parser.add_argument('--bg_img', type=str, default='white', help="background image")
    parser.add_argument('--fbg', action='store_true', help="frame-wise bg")
    parser.add_argument('--exp_eye', action='store_true', help="explicitly control the eyes")
    parser.add_argument('--fix_eye', type=float, default=-1,
                        help="fixed eye area, negative to disable, set to 0-0.3 for a reasonable eye")
    parser.add_argument('--smooth_eye', action='store_true', help="smooth the eye area sequence")

    parser.add_argument('--torso_shrink', type=float, default=0.8,
                        help="shrink bg coords to allow more flexibility in deform")

    ### dataset options
    parser.add_argument('--color_space', type=str, default='srgb', help="Color space, supports (linear, srgb)")
    parser.add_argument('--preload', type=int, default=0,
                        help="0 means load data from disk on-the-fly, 1 means preload to CPU, 2 means GPU.")
    # (the default value is for the fox dataset)
    parser.add_argument('--bound', type=float, default=1,
                        help="assume the scene is bounded in box[-bound, bound]^3, if > 1, will invoke adaptive ray marching.")
    parser.add_argument('--scale', type=float, default=4, help="scale camera location into box[-bound, bound]^3")
    parser.add_argument('--offset', type=float, nargs='*', default=[0, 0, 0], help="offset of camera location")
    parser.add_argument('--dt_gamma', type=float, default=1 / 256,
                        help="dt_gamma (>=0) for adaptive ray marching. set to 0 to disable, >0 to accelerate rendering (but usually with worse quality)")
    parser.add_argument('--min_near', type=float, default=0.05, help="minimum near distance for camera")
    parser.add_argument('--density_thresh', type=float, default=10,
                        help="threshold for density grid to be occupied (sigma)")
    parser.add_argument('--density_thresh_torso', type=float, default=0.01,
                        help="threshold for density grid to be occupied (alpha)")
    parser.add_argument('--patch_size', type=int, default=1,
                        help="[experimental] render patches in training, so as to apply LPIPS loss. 1 means disabled, use [64, 32, 16] to enable")

    parser.add_argument('--init_lips', action='store_true', help="init lips region")
    parser.add_argument('--finetune_lips', action='store_true', help="use LPIPS and landmarks to fine tune lips region")
    parser.add_argument('--smooth_lips', action='store_true', help="smooth the enc_a in a exponential decay way...")

    parser.add_argument('--torso', action='store_true', help="fix head and train torso")
    parser.add_argument('--head_ckpt', type=str, default='', help="head model")

    ### GUI options
    parser.add_argument('--gui', action='store_true', help="start a GUI")
    parser.add_argument('--W', type=int, default=450, help="GUI width")
    parser.add_argument('--H', type=int, default=450, help="GUI height")
    parser.add_argument('--radius', type=float, default=3.35, help="default GUI camera radius from center")
    parser.add_argument('--fovy', type=float, default=21.24, help="default GUI camera fovy")
    parser.add_argument('--max_spp', type=int, default=1, help="GUI rendering max sample per pixel")

    ### else
    parser.add_argument('--att', type=int, default=2,
                        help="audio attention mode (0 = turn off, 1 = left-direction, 2 = bi-direction)")
    parser.add_argument('--aud', type=str, default='',
                        help="audio source (empty will load the default, else should be a path to a npy file)")
    parser.add_argument('--emb', action='store_true', help="use audio class + embedding instead of logits")

    parser.add_argument('--ind_dim', type=int, default=4, help="individual code dim, 0 to turn off")
    parser.add_argument('--ind_num', type=int, default=10000,
                        help="number of individual codes, should be larger than training dataset size")

    parser.add_argument('--ind_dim_torso', type=int, default=8, help="individual code dim, 0 to turn off")

    parser.add_argument('--amb_dim', type=int, default=2, help="ambient dimension")
    parser.add_argument('--part', action='store_true', help="use partial training data (1/10)")
    parser.add_argument('--part2', action='store_true', help="use partial training data (first 15s)")

    parser.add_argument('--train_camera', action='store_true', help="optimize camera pose")
    parser.add_argument('--smooth_path', action='store_true',
                        help="brute-force smooth camera pose trajectory with a window size")
    parser.add_argument('--smooth_path_window', type=int, default=7, help="smoothing window size")

    # asr
    parser.add_argument('--asr', action='store_true', help="load asr for real-time app")
    parser.add_argument('--asr_wav', type=str, default='', help="load the wav and use as input")
    parser.add_argument('--asr_play', action='store_true', help="play out the audio")

    # parser.add_argument('--asr_model', type=str, default='deepspeech')
    parser.add_argument('--asr_model', type=str, default='cpierse/wav2vec2-large-xlsr-53-esperanto')  #
    # parser.add_argument('--asr_model', type=str, default='facebook/wav2vec2-large-960h-lv60-self')
    # parser.add_argument('--asr_model', type=str, default='facebook/hubert-large-ls960-ft')

    parser.add_argument('--asr_save_feats', action='store_true')
    # audio FPS
    parser.add_argument('--fps', type=int, default=50)
    # sliding window left-middle-right length (unit: 20ms)
    parser.add_argument('-l', type=int, default=10)
    parser.add_argument('-m', type=int, default=8)
    parser.add_argument('-r', type=int, default=10)

    parser.add_argument('--fullbody', action='store_true', help="fullbody human")
    parser.add_argument('--fullbody_img', type=str, default='data/fullbody/img')
    parser.add_argument('--fullbody_width', type=int, default=580)
    parser.add_argument('--fullbody_height', type=int, default=1080)
    parser.add_argument('--fullbody_offset_x', type=int, default=0)
    parser.add_argument('--fullbody_offset_y', type=int, default=0)

    # musetalk opt
    parser.add_argument('--avatar_id', type=str, default='avator_1')
    parser.add_argument('--bbox_shift', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=16)

    # parser.add_argument('--customvideo', action='store_true', help="custom video")
    # parser.add_argument('--customvideo_img', type=str, default='data/customvideo/img')
    # parser.add_argument('--customvideo_imgnum', type=int, default=1)

    parser.add_argument('--customvideo_config', type=str, default='')

    parser.add_argument('--tts', type=str, default='gpt-sovits')  # edgetts xtts gpt-sovits cosyvoice
    parser.add_argument('--REF_FILE', type=str, default=None)
    parser.add_argument('--REF_TEXT', type=str, default=None)
    parser.add_argument('--TTS_SERVER', type=str, default='http://146.56.226.252:5005')  # http://localhost:9000
    # parser.add_argument('--CHARACTER', type=str, default='test')
    # parser.add_argument('--EMOTION', type=str, default='default')

    parser.add_argument('--model', type=str, default='wav2lip')  # musetalk wav2lip

    parser.add_argument('--transport', type=str, default='rtcpush')  # rtmp webrtc rtcpush
    parser.add_argument('--push_url', type=str,
                        default='http://localhost:1985/rtc/v1/whip/?app=live&stream=livestream')  # rtmp://localhost/live/livestream

    parser.add_argument('--max_session', type=int, default=1)  # multi session count
    parser.add_argument('--listenport', type=int, default=8010)
    parser.add_argument('--ws_uri', type=str, default='ws://localhost:8877/ws')
    opt = parser.parse_args()
    # app.config.from_object(opt)
    # print(app.config)
    opt.customopt = []
    if opt.customvideo_config != '':
        with open(opt.customvideo_config, 'r') as file:
            opt.customopt = json.load(file)

    if opt.model == 'ernerf':
        from nerfreal import NeRFReal, load_model, load_avatar

        model = load_model(opt)
        avatar = load_avatar(opt)

        # we still need test_loader to provide audio features for testing.
        # for k in range(opt.max_session):
        #     opt.sessionid=k
        #     nerfreal = NeRFReal(opt, trainer, test_loader,audio_processor,audio_model)
        #     nerfreals.append(nerfreal)
    elif opt.model == 'musetalk':
        from musereal import MuseReal, load_model, load_avatar, warm_up

        print(opt)
        model = load_model()
        avatar = load_avatar(opt.avatar_id)
        warm_up(opt.batch_size, model)
        # for k in range(opt.max_session):
        #     opt.sessionid=k
        #     nerfreal = MuseReal(opt,audio_processor,vae, unet, pe,timesteps)
        #     nerfreals.append(nerfreal)
    elif opt.model == 'wav2lip':
        # from lipreal import LipReal,load_model,load_avatar
        from lipreal import LipReal, load_model, load_avatar, warm_up

        print(opt)
        model = load_model("./models/wav2lip.pth")
        # avatar = load_avatar(opt.avatar_id)
        warm_up(opt.batch_size, model, 256)
        # for k in range(opt.max_session):
        #     opt.sessionid=k
        #     nerfreal = LipReal(opt,model)
        #     nerfreals.append(nerfreal)
    elif opt.model == 'wav2lipls':
        from liplsreal import load_model,load_avatar,warm_up
        print(opt)
        model = load_model("./models/checkpoint_step000562000.pth")
        # avatar = load_avatar(opt.avatar_id)
        warm_up(opt.batch_size,model,192)
    if opt.transport == 'rtmp':
        thread_quit = Event()
        nerfreals[0] = build_nerfreal(0)
        rendthrd = Thread(target=nerfreals[0].render, args=(thread_quit,))
        rendthrd.start()

    #############################################################################
    appasync = web.Application(client_max_size=400 * 1024 * 1024)
    appasync.on_shutdown.append(on_shutdown)
    appasync.router.add_post("/offer", offer)
    appasync.router.add_post("/human", human)
    appasync.router.add_post("/humanaudio", humanaudio)
    appasync.router.add_post("/set_audiotype", set_audiotype)
    appasync.router.add_post("/record", record)
    appasync.router.add_post("/is_speaking", is_speaking)
    appasync.router.add_post("/switch_radio", switch_radio)
    appasync.router.add_post("/create_preloader", create_preloader)
    appasync.router.add_post("/delete_preloader", delete_preloader)
    appasync.router.add_post("/prewav2lip", prewav2lip)
    appasync.router.add_get("/ws", websocket_handler)
    appasync.router.add_get("/sse", sse_handler)
    appasync.router.add_static('/', path='web')

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(appasync, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    # Configure CORS on all routes.
    for route in list(appasync.router.routes()):
        cors.add(route)

    print('start http server; http://<serverip>:' + str(opt.listenport) + '/' + "webrtcapi-audiochat.html")


    ## 证书配置
    # import ssl
    # # 创建 SSL 上下文
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(certfile='web/certificate.crt',
    #                             keyfile='web/private.key')

    def run_server(runner):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        # site = web.TCPSite(runner, '0.0.0.0', opt.listenport, ssl_context=ssl_context)
        site = web.TCPSite(runner, '0.0.0.0', opt.listenport)
        loop.run_until_complete(site.start())
        # if opt.transport == 'rtcpush':
        #     for k in range(opt.max_session):
        #         push_url = opt.push_url
        #         if k != 0:
        #             push_url = opt.push_url + str(k)
        #         loop.run_until_complete(run(push_url, k))
        loop.run_forever()
        # Thread(target=run_server, args=(web.AppRunner(appasync),)).start()


    run_server(web.AppRunner(appasync))

    # app.on_shutdown.append(on_shutdown)
    # app.router.add_post("/offer", offer)

    # print('start websocket server')
    # server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    # server.serve_forever()

