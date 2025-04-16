<template>
  <div class="avatar-container">
    <div class="page-header">
      <h2>形象配置</h2>
      <el-button type="primary" @click="handleCreateAvatar">添加形象配置</el-button>
    </div>

    <el-table :data="avatarList" style="width: 100%" v-loading="loading">
      <el-table-column prop="avatar_uuid" label="UUID" width="220" />
      <el-table-column prop="name" label="名称" width="180" />
      <el-table-column prop="model_type" label="模型类型" width="120">
        <template #default="scope">
          <el-tag>{{ getModelTypeName(scope.row.model_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="small" type="primary" @click="handleActionConfig(scope.row)">动作配置</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑形象配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑形象配置' : '添加形象配置'"
      width="60%">
      <el-form :model="avatarForm" label-width="120px">
        <el-form-item label="形象名称">
          <el-input v-model="avatarForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="avatarForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="模型类型">
          <el-select v-model="avatarForm.model_type" placeholder="请选择模型类型">
            <el-option :label="'2D模型'" :value="1" />
            <el-option :label="'3D模型'" :value="2" />
            <el-option :label="'真人模型'" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型文件">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/model"
            :show-file-list="false"
            :on-success="handleModelSuccess"
            :before-upload="beforeModelUpload">
            <el-button type="primary">上传模型文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                请上传模型文件，支持的格式取决于模型类型
              </div>
            </template>
          </el-upload>
          <div v-if="avatarForm.model_path" class="model-preview">
            <span>已上传: {{ avatarForm.model_path }}</span>
            <el-button type="danger" size="small" @click="avatarForm.model_path = ''">删除</el-button>
          </div>
        </el-form-item>
        <el-form-item label="缩略图">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/image"
            :show-file-list="false"
            :on-success="handleThumbnailSuccess"
            :before-upload="beforeThumbnailUpload">
            <img v-if="avatarForm.thumbnail" :src="avatarForm.thumbnail" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="多模态配置" v-if="avatarForm.model_type === 3">
          <el-collapse>
            <el-collapse-item title="多模态大模型配置" name="1">
              <el-form-item label="选择LLM模型">
                <el-select v-model="avatarForm.multimodal_config.llm_uuid" placeholder="请选择LLM模型">
                  <el-option 
                    v-for="item in llmOptions" 
                    :key="item.llm_uuid" 
                    :label="item.name" 
                    :value="item.llm_uuid" />
                </el-select>
              </el-form-item>
              <el-form-item label="视觉处理">
                <el-switch v-model="avatarForm.multimodal_config.vision_enabled" />
              </el-form-item>
              <el-form-item label="音频处理">
                <el-switch v-model="avatarForm.multimodal_config.audio_enabled" />
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAvatarForm">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 动作配置对话框 -->
    <el-dialog
      v-model="actionDialogVisible"
      title="动作配置"
      width="70%">
      <div class="action-config-container">
        <div class="action-list">
          <h3>动作列表</h3>
          <el-button type="primary" size="small" @click="handleAddAction">添加动作</el-button>
          <el-table :data="actionList" style="width: 100%" height="400">
            <el-table-column prop="action_name" label="动作名称" />
            <el-table-column prop="trigger_type" label="触发类型">
              <template #default="scope">
                <el-tag>{{ getTriggerTypeName(scope.row.trigger_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="handleEditAction(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteAction(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="action-editor" v-if="showActionEditor">
          <h3>{{ isEditAction ? '编辑动作' : '添加动作' }}</h3>
          <el-form :model="actionForm" label-width="100px">
            <el-form-item label="动作名称">
              <el-input v-model="actionForm.action_name" />
            </el-form-item>
            <el-form-item label="触发类型">
              <el-select v-model="actionForm.trigger_type" placeholder="请选择触发类型">
                <el-option :label="'情绪触发'" :value="1" />
                <el-option :label="'关键词触发'" :value="2" />
                <el-option :label="'手动触发'" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item label="触发条件" v-if="actionForm.trigger_type === 1">
              <el-select v-model="actionForm.trigger_condition.emotion" placeholder="请选择情绪">
                <el-option label="开心" value="happy" />
                <el-option label="悲伤" value="sad" />
                <el-option label="愤怒" value="angry" />
                <el-option label="惊讶" value="surprised" />
              </el-select>
            </el-form-item>
            <el-form-item label="触发关键词" v-if="actionForm.trigger_type === 2">
              <el-input v-model="actionForm.trigger_condition.keyword" placeholder="请输入触发关键词" />
            </el-form-item>
            <el-form-item label="动作序列">
              <el-button size="small" @click="handleAddSequence">添加序列</el-button>
              <div v-for="(seq, index) in actionForm.sequences" :key="index" class="sequence-item">
                <el-input-number v-model="seq.time" :min="0" :step="0.1" label="时间点(秒)" />
                <el-select v-model="seq.action_type" placeholder="动作类型">
                  <el-option label="表情" value="expression" />
                  <el-option label="姿势" value="pose" />
                  <el-option label="移动" value="movement" />
                </el-select>
                <el-input v-model="seq.action_value" placeholder="动作值" />
                <el-button type="danger" size="small" @click="removeSequence(index)">删除</el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitActionForm">保存动作</el-button>
              <el-button @click="cancelActionEdit">取消</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 形象列表数据
const loading = ref(false)
const avatarList = ref([])

// 表单相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const avatarForm = reactive({
  avatar_uuid: '',
  name: '',
  description: '',
  model_type: 1,
  model_path: '',
  thumbnail: '',
  multimodal_config: {
    llm_uuid: '',
    vision_enabled: false,
    audio_enabled: false
  }
})

// LLM模型选项
const llmOptions = ref([])

// 获取模型类型名称
const getModelTypeName = (type) => {
  const typeMap = {
    1: '2D模型',
    2: '3D模型',
    3: '真人模型'
  }
  return typeMap[type] || '未知类型'
}

// 获取触发类型名称
const getTriggerTypeName = (type) => {
  const typeMap = {
    1: '情绪触发',
    2: '关键词触发',
    3: '手动触发'
  }
  return typeMap[type] || '未知类型'
}

// 获取形象配置列表
const fetchAvatarList = async () => {
  loading.value = true
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch('/api/avatar')
    const data = await response.json()
    if (data.code === 0) {
      avatarList.value = data.data
    } else {
      ElMessage.error(data.message || '获取形象配置列表失败')
    }
  } catch (error) {
    console.error('获取形象配置列表出错:', error)
    ElMessage.error('获取形象配置列表失败')
  } finally {
    loading.value = false
  }
}

// 获取LLM模型选项
const fetchLLMOptions = async () => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch('/api/llm')
    const data = await response.json()
    if (data.code === 0) {
      llmOptions.value = data.data
    } else {
      ElMessage.error(data.message || '获取LLM模型列表失败')
    }
  } catch (error) {
    console.error('获取LLM模型列表出错:', error)
    ElMessage.error('获取LLM模型列表失败')
  }
}

// 上传模型文件前的验证
const beforeModelUpload = (file) => {
  // 根据模型类型验证文件格式
  let isValidFormat = true
  const isLt100M = file.size / 1024 / 1024 < 100

  if (!isValidFormat) {
    ElMessage.error('上传模型文件格式不正确!')
  }
  if (!isLt100M) {
    ElMessage.error('上传模型文件大小不能超过100MB!')
  }
  return isValidFormat && isLt100M
}

// 模型文件上传成功回调
const handleModelSuccess = (response) => {
  if (response.code === 0) {
    avatarForm.model_path = response.data.path
    ElMessage.success('模型文件上传成功')
  } else {
    ElMessage.error(response.message || '模型文件上传失败')
  }
}

// 上传缩略图前的验证
const beforeThumbnailUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('上传缩略图只能是图片格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传缩略图大小不能超过2MB!')
  }
  return isImage && isLt2M
}

// 缩略图上传成功回调
const handleThumbnailSuccess = (response) => {
  if (response.code === 0) {
    avatarForm.thumbnail = response.data.url
    ElMessage.success('缩略图上传成功')
  } else {
    ElMessage.error(response.message || '缩略图上传失败')
  }
}

// 创建形象配置
const handleCreateAvatar = () => {
  isEdit.value = false
  avatarForm.avatar_uuid = ''
  avatarForm.name = ''
  avatarForm.description = ''
  avatarForm.model_type = 1
  avatarForm.model_path = ''
  avatarForm.thumbnail = ''
  avatarForm.multimodal_config = {
    llm_uuid: '',
    vision_enabled: false,
    audio_enabled: false
  }
  dialogVisible.value = true
}

// 编辑形象配置
const handleEdit = (row) => {
  isEdit.value = true
  avatarForm.avatar_uuid = row.avatar_uuid
  avatarForm.name = row.name
  avatarForm.description = row.description
  avatarForm.model_type = row.model_type
  avatarForm.model_path = row.model_path
  avatarForm.thumbnail = row.thumbnail
  avatarForm.multimodal_config = row.multimodal_config || {
    llm_uuid: '',
    vision_enabled: false,
    audio_enabled: false
  }
  dialogVisible.value = true
}

// 删除形象配置
const handleDelete = async (row) => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(`/api/avatar/${row.avatar_uuid}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success('删除成功')
      fetchAvatarList()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除形象配置出错:', error)
    ElMessage.error('删除失败')
  }
}

// 提交形象配置表单
const submitAvatarForm = async () => {
  try {
    const url = isEdit.value ? `/api/avatar/${avatarForm.avatar_uuid}` : '/api/avatar'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(avatarForm)
    })
    
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchAvatarList()
    } else {
      ElMessage.error(data.message || (isEdit.value ? '更新失败' : '创建失败'))
    }
  } catch (error) {
    console.error('提交形象配置表单出错:', error)
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

// 动作配置相关
const actionDialogVisible = ref(false)
const currentAvatarUUID = ref('')
const actionList = ref([])
const showActionEditor = ref(false)
const isEditAction = ref(false)
const actionForm = reactive({
  action_id: '',
  action_name: '',
  trigger_type: 1,
  trigger_condition: {
    emotion: 'happy',
    keyword: ''
  },
  sequences: []
})

// 打开动作配置对话框
const handleActionConfig = async (row) => {
  currentAvatarUUID.value = row.avatar_uuid
  actionDialogVisible.value = true
  showActionEditor.value = false
  await fetchActionList()
}

// 获取动作列表
const fetchActionList = async () => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(`/api/avatar/${currentAvatarUUID.value}/actions`)
    const data = await response.json()
    if (data.code === 0) {
      actionList.value = data.data
    } else {
      ElMessage.error(data.message || '获取动作列表失败')
    }
  } catch (error) {
    console.error('获取动作列表出错:', error)
    ElMessage.error('获取动作列表失败')
  }
}

// 添加动作
const handleAddAction = () => {
  isEditAction.value = false
  actionForm.action_id = ''
  actionForm.action_name = ''
  actionForm.trigger_type = 1
  actionForm.trigger_condition = {
    emotion: 'happy',
    keyword: ''
  }
  actionForm.sequences = []
  showActionEditor.value = true
}

// 编辑动作
const handleEditAction = (row) => {
  isEditAction.value = true
  actionForm.action_id = row.action_id
  actionForm.action_name = row.action_name
  actionForm.trigger_type = row.trigger_type
  actionForm.trigger_condition = row.trigger_condition || {
    emotion: 'happy',
    keyword: ''
  }
  actionForm.sequences = row.sequences || []
  showActionEditor.value = true
}

// 删除动作
const handleDeleteAction = async (row) => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(`/api/avatar/${currentAvatarUUID.value}/actions/${row.action_id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success('删除成功')
      fetchActionList()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除动作出错:', error)
    ElMessage.error('删除失败')
  }
}

// 添加动作序列
const handleAddSequence = () => {
  actionForm.sequences.push({
    time: 0,
    action_type: 'expression',
    action_value: ''
  })
}

// 移除动作序列
const removeSequence = (index) => {
  actionForm.sequences.splice(index, 1)
}

// 提交动作表单
const submitActionForm = async () => {
  try {
    const url = isEditAction.value 
      ? `/api/avatar/${currentAvatarUUID.value}/actions/${actionForm.action_id}` 
      : `/api/avatar/${currentAvatarUUID.value}/actions`
    const method = isEditAction.value ? 'PUT' : 'POST'
    
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(actionForm)
    })
    
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success(isEditAction.value ? '更新成功' : '创建成功')
      showActionEditor.value = false
      fetchActionList()
    } else {
      ElMessage.error(data.message || (isEditAction.value ? '更新失败' : '创建失败'))
    }
  } catch (error) {
    console.error('提交动作表单出错:', error)
    ElMessage.error(isEditAction.value ? '更新失败' : '创建失败')
  }
}

// 取消动作编辑
const cancelActionEdit = () => {
  showActionEditor.value = false
}

onMounted(() => {
  fetchAvatarList()
  fetchLLMOptions()
})
</script>

<style scoped>
.avatar-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.model-preview {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-config-container {
  display: flex;
  gap: 20px;
}

.action-list {
  flex: 1;
}

.action-editor {
  flex: 1;
  border-left: 1px solid #eee;
  padding-left: 20px;
}

.sequence-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}
</style>