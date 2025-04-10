import asyncio
import json
from typing import Tuple, Dict, Optional, Set, Union
from av import AudioFrame,AudioLayout,AudioResampler
import numpy as np
import time
import os
import traceback
from aiortc import (
    MediaStreamTrack,
)
from asr.funasr_client_api import Funasr_websocket_recognizer

def llm_response(message,nerfreal):
    start = time.perf_counter()
    from openai import OpenAI
    client = OpenAI(
        # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        # api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_key="sk-39d9ee26cd1e4103aeb065242532599a",
        # 填写DashScope SDK的base_url
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    end = time.perf_counter()
    print(f"llm Time init: {end-start}s")
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                  {'role': 'user', 'content': message}],
        stream=True,
        # 通过以下设置，在流式输出的最后一行展示token使用信息
        stream_options={"include_usage": True}
    )
    result=""
    first = True
    for chunk in completion:
        if len(chunk.choices)>0:
            #print(chunk.choices[0].delta.content)
            if first:
                end = time.perf_counter()
                print(f"llm Time to first chunk: {end-start}s")
                first = False
            msg = chunk.choices[0].delta.content
            lastpos=0
            #msglist = re.split('[,.!;:，。！?]',msg)
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；" :
                    result = result+msg[lastpos:i+1]
                    lastpos = i+1
                    if len(result)>10:
                        print(result)
                        nerfreal.put_msg_txt(result)
                        result=""
            result = result+msg[lastpos:]
    end = time.perf_counter()
    print(f"llm Time to last chunk: {end-start}s")
    nerfreal.put_msg_txt(result)  

class RtcRecv:
    """
    A media sink that recv audio 
    """

    def __init__(self, nerfreal):
        self.__container = nerfreal
        #self.__tracks = {}
        self._track = None
        self._task = None
        self._bytes = b''

    def addTrack(self, track: MediaStreamTrack) -> None:
        """
        Add a track to be recv.

        :param track: A :class:`aiortc.MediaStreamTrack`.
        """
        if track.kind == "audio":
            self._track = track

    async def start(self) -> None:
        """
        Start recv.
        """
        if self._track is not None and self._task is None:
            self._task = asyncio.ensure_future(self.__run_track(self._track))

        # create an asr recognizer
        chunk_size = "5,10,5"
        chunk_interval=10
        self._rcg = Funasr_websocket_recognizer(
            # host="www.funasr.com",
            # host="localhost",
            host="localhost",
            port="10096", is_ssl=True, mode="2pass", chunk_size = chunk_size,
            chunk_interval = chunk_interval, wav_name = 'microphone'
        )
        RATE = 16000
        chunk_size = [int(x) for x in chunk_size.split(",")]
        self._asrchunksize = 60 * chunk_size[1] / chunk_interval
        self._asrchunksize = int(RATE / 1000 * self._asrchunksize*2)

    async def stop(self) -> None:
        """
        Stop recv.
        """
        if self._track is not None and self._task is not None:
            self._task.cancel()
            self._task = None
        self._track = None
        # get last message
        text = self._rcg.close(timeout=1)
        #with open('test.pcm', 'wb') as file:
        #    file.write(self._bytes)

    async def __run_track(
        self, track: MediaStreamTrack
    ) -> None:
        return
        audio_sample_rate = 16000
        audio_resampler = AudioResampler(
            format="s16",
            layout="mono", #"stereo",
            rate=audio_sample_rate,
            frame_size=int(audio_sample_rate * 0.06),
        )
        laststate = ''
        while True:
            try:
                origframe: AudioFrame = await track.recv()
                for frame in audio_resampler.resample(origframe):
                    stream = frame.to_ndarray()
                    if self.__container.stop_radio:
                        continue
                    asrmsg = self._rcg.feed_chunk(stream.tobytes()) 
                    if len(asrmsg) > 0:
                        if asrmsg['mode'] == '2pass-offline':
                            asr_text = asrmsg['text']
                            print(asr_text)
                            # await self.__container.dcqueue.clear()
                            await self.__container.clear_queue(self.__container.dcqueue)
                            self.__container.sendmessage(json.dumps({"type":"user", "content": asr_text}, ensure_ascii=False))
                            # await self.__container.dcqueue.put({"type":"user", "content": asr_text})
                            self.__container.flush_talk()
                            await asyncio.get_event_loop().run_in_executor(None, llm_response, asr_text,self.__container)
            except Exception as e: #MediaStreamError:
                traceback.print_exc()
                return

            # for packet in context.stream.encode(frame):
            #     self.__container.mux(packet)