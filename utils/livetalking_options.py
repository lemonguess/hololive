class Opt:
    def __init__(self):
        # 路径参数
        self.pose = "source/data/data_kf.json"
        self.au = "source/data/au.csv"
        self.torso_imgs = ""
        self.workspace = "source/data/video"
        self.ckpt = "source/data/pretrained/ngp_kf.pth"
        self.head_ckpt = ""
        self.aud = ""
        self.asr_wav = ""
        self.fullbody_img = "source/data/fullbody/img"
        self.customvideo_config = ""
        self.REF_FILE = None
        self.REF_TEXT = None
        self.TTS_SERVER = "http://146.56.226.252:5005"
        self.push_url = "http://localhost:1985/rtc/v1/whip/?app=live&stream=livestream"
        self.ws_uri = "ws://localhost:8877/ws"

        # 训练选项
        self.O = False
        self.data_range = [0, -1]
        self.seed = 0
        self.num_rays = 4096 * 16
        self.cuda_ray = False
        self.max_steps = 16
        self.num_steps = 16
        self.upsample_steps = 0
        self.update_extra_interval = 16
        self.max_ray_batch = 4096
        self.warmup_step = 10000
        self.amb_aud_loss = 1
        self.amb_eye_loss = 1
        self.unc_loss = 1
        self.lambda_amb = 1e-4
        self.fp16 = False
        self.preload = 0
        self.patch_size = 1

        # 功能开关
        self.gui = False
        self.fbg = False
        self.exp_eye = False
        self.smooth_eye = False
        self.init_lips = False
        self.finetune_lips = False
        self.smooth_lips = False
        self.torso = False
        self.emb = False
        self.part = False
        self.part2 = False
        self.train_camera = False
        self.smooth_path = False
        self.asr = False
        self.asr_play = False
        self.asr_save_feats = False
        self.fullbody = False

        # 数值参数
        self.fix_eye = -1
        self.torso_shrink = 0.8
        self.bound = 1
        self.scale = 4
        self.offset = [0, 0, 0]
        self.dt_gamma = 1 / 256
        self.min_near = 0.05
        self.density_thresh = 10
        self.density_thresh_torso = 0.01
        self.att = 2
        self.ind_dim = 4
        self.ind_num = 10000
        self.ind_dim_torso = 8
        self.amb_dim = 2
        self.smooth_path_window = 7
        self.fps = 50
        self.l = 10
        self.m = 8
        self.r = 10
        self.fullbody_width = 580
        self.fullbody_height = 1080
        self.fullbody_offset_x = 0
        self.fullbody_offset_y = 0
        self.avatar_id = "avator_1"
        self.bbox_shift = 5
        self.batch_size = 16
        self.max_session = 1
        self.listenport = 8010

        # 字符串参数
        self.bg_img = "white"
        self.color_space = "srgb"
        self.asr_model = "cpierse/wav2vec2-large-xlsr-53-esperanto"
        self.tts = "gpt-sovits"
        self.model = "wav2lip"
        self.transport = "rtcpush"

        # GUI参数
        self.W = 450
        self.H = 450
        self.radius = 3.35
        self.fovy = 21.24
        self.max_spp = 1