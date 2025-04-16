<template>
  <div class="llm-container">
    <div class="page-header">
      <h2>LLM模型管理</h2>
      <el-button type="primary" @click="handleCreateLLM">添加LLM模型</el-button>
    </div>

    <el-table :data="llmList" style="width: 100%" v-loading="loading">
      <el-table-column prop="llm_uuid" label="UUID" width="220" />
      <el-table-column prop="name" label="名称" width="180" />
      <el-table-column prop="provider_name" label="供应商" width="150" />
      <el-table-column prop="max_tokens" label="最大Token" width="120" />
      <el-table-column prop="context_length" label="上下文长度" width="120" />
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑LLM模型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑LLM模型' : '添加LLM模型'"
      width="50%">
      <el-form :model="llmForm" label-width="120px">
        <el-form-item label="模型名称">
          <el-input v-model="llmForm.name" />
        </el-form-item>
        <el-form-item label="选择供应商">
          <el-select v-model="llmForm.user_provider_uuid" placeholder="请选择供应商">
            <el-option 
              v-for="item in providerOptions" 
              :key="item.user_provider_uuid" 
              :label="item.name" 
              :value="item.user_provider_uuid" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大Token">
          <el-input-number v-model="llmForm.max_tokens" :min="1" :max="100000" />
        </el-form-item>
        <el-form-item label="上下文长度">
          <el-input-number v-model="llmForm.context_length" :min="1" :max="100000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitLLMForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// LLM模型列表数据
const loading = ref(false)
const llmList = ref([])

// 表单相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const llmForm = reactive({
  llm_uuid: '',
  name: '',
  user_provider_uuid: '',
  max_tokens: 2048,
  context_length: 4096
})

// 供应商选项
const providerOptions = ref([])

// 获取LLM模型列表
const fetchLLMList = async () => {
  loading.value = true
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch('/api/llm')
    const data = await response.json()
    if (data.code === 0) {
      llmList.value = data.data
    } else {
      ElMessage.error(data.message || '获取LLM模型列表失败')
    }
  } catch (error) {
    console.error('获取LLM模型列表出错:', error)
    ElMessage.error('获取LLM模型列表失败')
  } finally {
    loading.value = false
  }
}

// 获取供应商选项
const fetchProviderOptions = async () => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch('/api/user/providers')
    const data = await response.json()
    if (data.code === 0) {
      providerOptions.value = data.data
    } else {
      ElMessage.error(data.message || '获取供应商列表失败')
    }
  } catch (error) {
    console.error('获取供应商列表出错:', error)
    ElMessage.error('获取供应商列表失败')
  }
}

// 创建LLM模型
const handleCreateLLM = () => {
  isEdit.value = false
  llmForm.llm_uuid = ''
  llmForm.name = ''
  llmForm.user_provider_uuid = ''
  llmForm.max_tokens = 2048
  llmForm.context_length = 4096
  dialogVisible.value = true
}

// 编辑LLM模型
const handleEdit = (row) => {
  isEdit.value = true
  llmForm.llm_uuid = row.llm_uuid
  llmForm.name = row.name
  llmForm.user_provider_uuid = row.user_provider_uuid
  llmForm.max_tokens = row.max_tokens
  llmForm.context_length = row.context_length
  dialogVisible.value = true
}

// 删除LLM模型
const handleDelete = async (row) => {
  try {
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(`/api/llm/${row.llm_uuid}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success('删除成功')
      fetchLLMList()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除LLM模型出错:', error)
    ElMessage.error('删除失败')
  }
}

// 提交LLM模型表单
const submitLLMForm = async () => {
  try {
    const url = isEdit.value ? `/api/llm/${llmForm.llm_uuid}` : '/api/llm'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    // 模拟API调用，实际项目中应替换为真实API
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(llmForm)
    })
    
    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchLLMList()
    } else {
      ElMessage.error(data.message || (isEdit.value ? '更新失败' : '创建失败'))
    }
  } catch (error) {
    console.error('提交LLM模型表单出错:', error)
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

onMounted(() => {
  fetchLLMList()
  fetchProviderOptions()
})
</script>

<style scoped>
.llm-container {
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
</style>