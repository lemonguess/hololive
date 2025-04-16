<template>
  <div class="tts-container">
    <div class="page-header">
      <h2>TTS配置</h2>
      <el-button type="primary" @click="handleCreateTTS">添加TTS配置</el-button>
    </div>

    <el-table :data="ttsList" style="width: 100%" v-loading="loading">
      <el-table-column prop="voice_uuid" label="UUID" width="220" />
      <el-table-column prop="name" label="名称" width="180" />
      <el-table-column prop="charactor" label="角色" width="120" />
      <el-table-column prop="default_language" label="默认语言" width="120" />
      <el-table-column prop="default_emotion" label="默认情绪" width="120" />
      <el-table-column prop="tts_type" label="TTS类型" width="120">
        <template #default="scope">
          <el-tag>{{ getTTSTypeName(scope.row.tts_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑TTS配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑TTS配置' : '添加TTS配置'"
      width="60%">
      <el-form :model="ttsForm" label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="ttsForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="ttsForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="TTS类型">
          <el-select v-model="ttsForm.tts_type" placeholder="请选择TTS类型">
            <el-option :label="'标准TTS'" :value="1" />
            <el-option :label="'情感TTS'" :value="2" />
            <el-option :label="'克隆TTS'" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-input v-model="ttsForm.charactor" />
        </el-form-item>
        <el-form-item label="默认语言">
          <el-select v-model="ttsForm.default_language" placeholder="请选择默认语言">
            <el-option label="中文" value="zh" />
            <el-option label="英文" value="en" />
            <el-option label="日文" value="jp" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认情绪">
          <el-select v-model="ttsForm.default_emotion" placeholder="请选择默认情绪">
            <el-option label="正常" value="normal" />
            <el-option label="开心" value="happy" />
            <el-option label="悲伤" value="sad" />
            <el-option label="愤怒" value="angry" />
            <el-option label="惊讶" value="surprised" />
          </el-select>
        </el-form-item>
        <el-form-item label="高级配置" v-if="ttsForm.tts_type > 1">
          <el-collapse>
            <el-collapse-item title="高级参数设置" name="1">
              <el-form-item label="音调">
                <el-slider v-model="ttsForm.configs.pitch" :min="0" :max="100" />
              </el-form-item>
              <el-form-item label="语速">
                <el-slider v-model="ttsForm.configs.speed" :min="0" :max="100" />
              </el-form-item>
              <el-form-item label="音量">
                <el-slider v-model="ttsForm.configs.volume" :min="0" :max="100" />
              </el-form-item>
              <el-form-item label="克隆音频" v-if="ttsForm.tts_type === 3">
                <el-upload
                  class="upload-demo"
                  action="/api/upload/audio"
                  :on-success="handleAudioSuccess"
                  :before-upload="beforeAudioUpload">
                  <el-button type="primary">上传克隆音频</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      请上传MP3或WAV格式的音频文件，用于声音克隆
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTTSForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// TTS配置列表数据
const loading = ref(false)
const ttsList = ref([])

// 表单相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const ttsForm = reactive({
  voice_uuid: '',
  name: '',
  description: '',
  tts_type: 1,
  charactor: '',
  default_emotion: 'normal',
  default_language: 'zh',
  configs: {
    pitch: 50,
    speed: 50,
    volume: 50,
    clone_audio: ''
  }
})

// 获取TTS类型名称
const getTTSTypeName = (type) => {
  const typeMap = {
    1: '标准TTS',
    2: '情感TTS',
    3: '克隆TTS'
  }
  return typeMap[type] || '未知类型'
}

// 获取TTS配置列表
const fetchTTSList = async () => {
  loading.value = true
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch('/api/tts')
    const data = await response.json()
    if (data.code === 0) {
      ttsList.value = data.data
    } else {
      ElMessage.error(data.message || '获取TTS配置列表失败')
    }
  } catch (error) {
    console.error('获取TTS配置列表出错:', error)
    ElMessage.error('获取TTS配置列表失败')
  } finally {
    loading.value = false
  }
}

// 创建TTS配置
const handleCreateTTS = () => {
  isEdit.value = false
  ttsForm.voice_uuid = ''
  ttsForm.name = ''
  ttsForm.description = ''
  ttsForm.tts_type = 1
  ttsForm.charactor = ''
  ttsForm.default_emotion = 'normal'
  ttsForm.default_language = 'zh'
  ttsForm.configs = {
    pitch: 50,
    speed: 50,
    volume: 50,
    clone_audio: ''
  }
  dialogVisible.value = true
}

// 编辑TTS配置
const handleEdit = (row) => {
  isEdit.value = true
  ttsForm.voice_uuid = row.voice_uuid
  ttsForm.name = row.name
  ttsForm.description = row.description
  ttsForm.tts_type = row.tts_type
  ttsForm.charactor = row.charactor
  ttsForm.default_emotion = row.default_emotion
  ttsForm.default_language = row.default_language
  ttsForm.configs = row.configs || {
    pitch: 50,
    speed: 50,
    volume: 50,
    clone_audio: ''
  }
  dialogVisible.value = true
}

// 删除TTS配置
const handleDelete = async (row) => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(`/api/tts/${row.voice_uuid}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success('删除成功')
      fetchTTSList()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除TTS配置出错:', error)
    ElMessage.error('删除失败')
  }
}

// 上传音频前的验证
const beforeAudioUpload = (file) => {
  const isAudio = file.type === 'audio/mp3' || file.type === 'audio/wav' || file.type === 'audio/mpeg'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isAudio) {
    ElMessage.error('上传音频只能是MP3/WAV格式!')
  }
  if (!isLt10M) {
    ElMessage.error('上传音频大小不能超过10MB!')
  }
  return isAudio && isLt10M
}

// 音频上传成功回调
const handleAudioSuccess = (response) => {
  if (response.code === 0) {
    ttsForm.configs.clone_audio = response.data.url
    ElMessage.success('音频上传成功')
  } else {
    ElMessage.error(response.message || '音频上传失败')
  }
}

// 提交TTS配置表单
const submitTTSForm = async () => {
  try {
    const url = isEdit.value ? `/api/tts/${ttsForm.voice_uuid}` : '/api/tts'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(ttsForm)
    })
    
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchTTSList()
    } else {
      ElMessage.error(data.message || (isEdit.value ? '更新失败' : '创建失败'))
    }
  } catch (error) {
    console.error('提交TTS配置表单出错:', error)
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

onMounted(() => {
  fetchTTSList()
})
</script>

<style scoped>
.tts-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.upload-demo {
  margin-top: 10px;
}
</style>