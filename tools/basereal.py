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
import json
import numpy as np
import subprocess
import os,sys
import time
import cv2
import glob
import resampy
from io import BytesIO
import soundfile as sf
import asyncio
import websocket
from ttsreal import EdgeTTS, VoitsTTS, XTTS, CosyVoiceTTS
from tqdm import tqdm

def read_imgs(img_list):
    frames = []
    print('reading images...')
    for img_path in tqdm(img_list):
        frame = cv2.imread(img_path)
        frames.append(frame)
    return frames


class BaseReal:
    def __init__(self, opt):
        self.opt = opt
        self.sample_rate = 16000
        self.chunk = self.sample_rate // opt.fps  # 320 samples per chunk (20ms * 16000 / 1000)
        self.sessionid = self.opt.sessionid

        if opt.tts == "edgetts":
            self.tts = EdgeTTS(opt, self)
        elif opt.tts == "gpt-sovits":
            self.tts = VoitsTTS(opt, self)
        elif opt.tts == "xtts":
            self.tts = XTTS(opt, self)
        elif opt.tts == "cosyvoice":
            self.tts = CosyVoiceTTS(opt, self)
        self.speaking = False
        self.recording = False
        self._record_video_pipe = None
        self._record_audio_pipe = None
        self.width = self.height = 0
        self.stop_radio = True
        self.curr_state = 0
        self.custom_img_cycle = {}
        self.custom_audio_cycle = {}
        self.custom_audio_index = {}
        self.custom_index = {}
        self.custom_opt = {}
        self.__loadcustom()
        self.main_playfile = ""
        self.last_task = "carousel"  # carousel or command
        self.last_audio_queue = None
        self.ws_uri = ""
        self.username = ""
        self.msg_queue = asyncio.Queue()
        self.start_event = asyncio.Event()
        self.stop_event = asyncio.Event()

    @staticmethod
    async def clear_queue(queue):
        while not queue.empty():
            try:
                queue.get_nowait()  # 获取并丢弃队列中的项目
            except asyncio.QueueEmpty:
                break  # 如果队列为空，则退出循环

    def put_msg_txt(self, msg):
        # self.flush_talk()
        self.tts.put_msg_txt(msg)
        self.last_task = "command"  # carousel or command
        self.sendmessage(json.dumps({"type": "system", "content": msg}, ensure_ascii=False))

    def put_audio_frame(self, audio_chunk):  # 16khz 20ms pcm
        self.asr.put_audio_frame(audio_chunk)

    def put_audio_file(self, filebyte):
        input_stream = BytesIO(filebyte)
        stream = self.__create_bytes_stream(input_stream)
        streamlen = stream.shape[0]
        idx = 0
        while streamlen >= self.chunk:  # and self.state==State.RUNNING
            self.put_audio_frame(stream[idx:idx + self.chunk])
            streamlen -= self.chunk
            idx += self.chunk

    def __create_bytes_stream(self, byte_stream):
        # byte_stream=BytesIO(buffer)
        stream, sample_rate = sf.read(byte_stream)  # [T*sample_rate,] float64
        # print(f'[INFO]put audio stream {sample_rate}: {stream.shape}')
        stream = stream.astype(np.float32)

        if stream.ndim > 1:
            # print(f'[WARN] audio has {stream.shape[1]} channels, only use the first.')
            stream = stream[:, 0]

        if sample_rate != self.sample_rate and stream.shape[0] > 0:
            # print(f'[WARN] audio sample rate is {sample_rate}, resampling into {self.sample_rate}.')
            stream = resampy.resample(x=stream, sr_orig=sample_rate, sr_new=self.sample_rate)
        return stream

    def set_main_play(self, main_playfile):
        self.main_playfile = main_playfile

    def set_datachannel(self, dcqueue, loop):
        self.dcqueue = dcqueue
        self.dcloop = loop

    def sendmessage(self, msg):
        if self.dcqueue:
            asyncio.run_coroutine_threadsafe(self.dcqueue.put(msg), self.dcloop)
            # asyncio.run_coroutine_threadsafe(self.datachannel.send(msg), self.rtcloop)
            # await self.rtcloop.run_in_executor(None, self.datachannel.send, msg)
        else:
            print('datachannel is none')

    @staticmethod
    def restore_queue(queue_obj, items):
        for item in items:
            queue_obj.put(item)  # 将元素放回队列

    @staticmethod
    def extract_all(queue_obj):
        items = []
        while not queue_obj.empty():
            items.append(queue_obj.get())  # 从队列中取出元素
        return items

    # 音频播放及打断处理逻辑线程
    def main_playthrd(self, quit_event):
        ws = websocket.create_connection(self.ws_uri)
        print(f"Connected to {self.ws_uri}")
        self.start_event.set()
        time.sleep(5)
        while not quit_event.is_set():
            try:
                if self.asr.queue.qsize() >= 30:  # 如果说话，等待
                    time.sleep(0.05)
                    continue
                ws.send(json.dumps({"user": self.username}, ensure_ascii=False))
                response = ws.recv()
                if "no wav" in response:
                    time.sleep(0.05)
                    continue
                print(f"Websocket Received: {response}")
                res_json = json.loads(response)
                print(res_json)
                playfile = res_json["Data"].get("Value")
                audio_text = res_json["Data"].get("Text", "")
                Image = res_json["Data"].get("Image", "")
                # mess_ty = res_json["Data"].get("Type")
                # image_url = urljoin("http://localhost:8877/", Image)
                # image_url = Image.replace('\\', '/').replace(':', '').replace('F', 'http://100.70.154.11:8877').replace("IIS/PX_IIS/", "")
                image_url = Image.replace('\\', '/').replace(':', '').replace('F', 'https://pinxin.s7.tunnelfrp.com').replace("IIS/PX_IIS/", "")
                print("image_url:::", image_url)
                # self.sendmessage(json.dumps({"type": "system", "content": mess_ty+"/"+audio_text}, ensure_ascii=False))
                # self.sendmessage(json.dumps({"type": "system", "content": audio_text}, ensure_ascii=False))
                # self.sendmessage(json.dumps({"type": "image", "content": image_url}, ensure_ascii=False))
                asyncio.run(self.msg_queue.put(json.dumps({"type": "system", "content": audio_text}, ensure_ascii=False)))
                asyncio.run(self.msg_queue.put(json.dumps({"type": "image", "content": image_url}, ensure_ascii=False)))
                main_playfile = playfile
                idx = 0
                stream = self.__create_bytes_stream(main_playfile)
                streamlen = len(stream)  # 假设stream是一个列表或数组
                while streamlen >= self.chunk:
                    self.put_audio_frame(stream[idx:idx + self.chunk])
                    streamlen -= self.chunk
                    idx += self.chunk
                while not self.is_speaking():  # 如果没说话，等待
                    time.sleep(0.5)
                    continue
            except websocket.WebSocketConnectionClosedException:
                print(f"Websocket connection closed for {self.ws_uri}")
                break
            except Exception as e:
                # print(e)
                time.sleep(0.05)
                continue
        ws.close()
        self.stop_event.set()

    def flush_talk(self):
        if self.last_task == "carousel":  # 备份音频队列
            self.last_audio_queue = self.extract_all(self.asr.queue)
        self.tts.flush_talk()
        self.asr.flush_talk()

    def is_speaking(self) -> bool:
        return self.speaking

    def __loadcustom(self):
        for item in self.opt.customopt:
            print(item)
            input_img_list = glob.glob(os.path.join(item['imgpath'], '*.[jpJP][pnPN]*[gG]'))
            input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            self.custom_img_cycle[item['audiotype']] = read_imgs(input_img_list)
            self.custom_audio_cycle[item['audiotype']], sample_rate = sf.read(item['audiopath'], dtype='float32')
            self.custom_audio_index[item['audiotype']] = 0
            self.custom_index[item['audiotype']] = 0
            self.custom_opt[item['audiotype']] = item

    def init_customindex(self):
        self.curr_state = 0
        for key in self.custom_audio_index:
            self.custom_audio_index[key] = 0
        for key in self.custom_index:
            self.custom_index[key] = 0

    def start_recording(self):
        """开始录制视频"""
        if self.recording:
            return

        command = ['ffmpeg',
                   '-y', '-an',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',  # 像素格式
                   '-s', "{}x{}".format(self.width, self.height),
                   '-r', str(25),
                   '-i', '-',
                   '-pix_fmt', 'yuv420p',
                   '-vcodec', "h264",
                   # '-f' , 'flv',
                   f'temp{self.opt.sessionid}.mp4']
        self._record_video_pipe = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE)

        acommand = ['ffmpeg',
                    '-y', '-vn',
                    '-f', 's16le',
                    # '-acodec','pcm_s16le',
                    '-ac', '1',
                    '-ar', '16000',
                    '-i', '-',
                    '-acodec', 'aac',
                    # '-f' , 'wav',
                    f'temp{self.opt.sessionid}.aac']
        self._record_audio_pipe = subprocess.Popen(acommand, shell=False, stdin=subprocess.PIPE)

        self.recording = True
        # self.recordq_video.queue.clear()
        # self.recordq_audio.queue.clear()
        # self.container = av.open(path, mode="w")

        # process_thread = Thread(target=self.record_frame, args=())
        # process_thread.start()

    def record_video_data(self, image):
        if self.width == 0:
            print("image.shape:", image.shape)
            self.height, self.width, _ = image.shape
        if self.recording:
            self._record_video_pipe.stdin.write(image.tostring())

    def record_audio_data(self, frame):
        if self.recording:
            self._record_audio_pipe.stdin.write(frame.tostring())

    # def record_frame(self):
    #     videostream = self.container.add_stream("libx264", rate=25)
    #     videostream.codec_context.time_base = Fraction(1, 25)
    #     audiostream = self.container.add_stream("aac")
    #     audiostream.codec_context.time_base = Fraction(1, 16000)
    #     init = True
    #     framenum = 0
    #     while self.recording:
    #         try:
    #             videoframe = self.recordq_video.get(block=True, timeout=1)
    #             videoframe.pts = framenum #int(round(framenum*0.04 / videostream.codec_context.time_base))
    #             videoframe.dts = videoframe.pts
    #             if init:
    #                 videostream.width = videoframe.width
    #                 videostream.height = videoframe.height
    #                 init = False
    #             for packet in videostream.encode(videoframe):
    #                 self.container.mux(packet)
    #             for k in range(2):
    #                 audioframe = self.recordq_audio.get(block=True, timeout=1)
    #                 audioframe.pts = int(round((framenum*2+k)*0.02 / audiostream.codec_context.time_base))
    #                 audioframe.dts = audioframe.pts
    #                 for packet in audiostream.encode(audioframe):
    #                     self.container.mux(packet)
    #             framenum += 1
    #         except queue.Empty:
    #             print('record queue empty,')
    #             continue
    #         except Exception as e:
    #             print(e)
    #             #break
    #     for packet in videostream.encode(None):
    #         self.container.mux(packet)
    #     for packet in audiostream.encode(None):
    #         self.container.mux(packet)
    #     self.container.close()
    #     self.recordq_video.queue.clear()
    #     self.recordq_audio.queue.clear()
    #     print('record thread stop')

    def stop_recording(self):
        """停止录制视频"""
        if not self.recording:
            return
        self.recording = False
        self._record_video_pipe.stdin.close()  # wait()
        self._record_video_pipe.wait()
        self._record_audio_pipe.stdin.close()
        self._record_audio_pipe.wait()
        cmd_combine_audio = f"ffmpeg -y -i temp{self.opt.sessionid}.aac -i temp{self.opt.sessionid}.mp4 -c:v copy -c:a copy data/record.mp4"
        os.system(cmd_combine_audio)
        # os.remove(output_path)

    def mirror_index(self, size, index):
        # size = len(self.coord_list_cycle)
        turn = index // size
        res = index % size
        if turn % 2 == 0:
            return res
        else:
            return size - res - 1

    def get_audio_stream(self, audiotype):
        idx = self.custom_audio_index[audiotype]
        stream = self.custom_audio_cycle[audiotype][idx:idx + self.chunk]
        self.custom_audio_index[audiotype] += self.chunk
        if self.custom_audio_index[audiotype] >= self.custom_audio_cycle[audiotype].shape[0]:
            self.curr_state = 1  # 当前视频不循环播放，切换到静音状态
        return stream

    def set_curr_state(self, audiotype, reinit):
        print('set_curr_state:', audiotype)
        self.curr_state = audiotype
        if reinit:
            self.custom_audio_index[audiotype] = 0
            self.custom_index[audiotype] = 0

    # def process_custom(self,audiotype:int,idx:int):
    #     if self.curr_state!=audiotype: #从推理切到口播
    #         if idx in self.switch_pos:  #在卡点位置可以切换
    #             self.curr_state=audiotype
    #             self.custom_index=0
    #     else:
    #         self.custom_index+=1

