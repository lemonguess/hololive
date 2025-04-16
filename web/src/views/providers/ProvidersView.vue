<template>
  <div class="providers-container">
    <div class="page-header">
      <h2>供应商管理</h2>
      <el-button type="primary" @click="handleCreateProvider">添加供应商</el-button>
    </div>

    <el-table :data="providerList" style="width: 100%" v-loading="loading">
      <el-table-column prop="provider_uuid" label="UUID" width="220" />
      <el-table-column prop="name" label="名称" width="180" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="small" type="primary" @click="handleConfigApiKey(scope.row)">配置API Key</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑供应商对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑供应商' : '添加供应商'"
      width="50%">
      <el-form :model="providerForm" label-width="120px">
        <el-form-item label="供应商名称">
          <el-input v-model="providerForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="providerForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="图标">
          <el-upload
            class="avatar-uploader"
            action="/api/upload"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload">
            <img v-if="providerForm.icon" :src="providerForm.icon" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitProviderForm">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 配置API Key对话框 -->
    <el-dialog
      v-model="apiKeyDialogVisible"
      title="配置API Key"
      width="50%">
      <el-form :model="apiKeyForm" label-width="120px">
        <el-form-item label="API Key">
          <el-input v-model="apiKeyForm.api_key" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="apiKeyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApiKeyForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 供应商列表数据
const loading = ref(false)
const providerList = ref([])

// 表单相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const providerForm = reactive({
  provider_uuid: '',
  name: '',
  description: '',
  icon: ''
})

// API Key相关
const apiKeyDialogVisible = ref(false)
const apiKeyForm = reactive({
  provider_uuid: '',
  api_key: ''
})

// 获取供应商列表
const fetchProviderList = async () => {
  loading.value = true
  try {
    // 模拟API调用
    setTimeout(() => {
      providerList.value = [
        {
          provider_uuid: 'provider-001',
          name: 'OpenAI',
          description: 'OpenAI API提供商，包含GPT系列模型',
          icon: 'https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg'
        },
        {
          provider_uuid: 'provider-002',
          name: 'Anthropic',
          description: 'Anthropic API提供商，包含Claude系列模型',
          icon: 'https://upload.wikimedia.org/wikipedia/commons/2/25/Anthropic_logo.svg'
        }
      ]
      loading.value = false
    }, 500)
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    ElMessage.error('获取供应商列表失败')
    loading.value = false
  }
}

// 创建供应