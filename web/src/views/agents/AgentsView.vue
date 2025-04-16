<template>
  <div class="agents-container">
    <div class="page-header">
      <h2>智能体管理</h2>
      <el-button type="primary" @click="handleCreateAgent">创建智能体</el-button>
    </div>

    <el-table :data="agentList" style="width: 100%" v-loading="loading">
      <el-table-column prop="agent_uuid" label="UUID" width="220" />
      <el-table-column prop="agent_name" label="名称" width="180" />
      <el-table-column prop="llm_name" label="使用模型" width="150" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="small" type="primary" @click="handleChat(scope.row)">对话</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑智能体对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑智能体' : '创建智能体'"
      width="60%">
      <el-form :model="agentForm" label-width="120px">
        <el-form-item label="智能体名称">
          <el-input v-model="agentForm.agent_name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="agentForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="选择LLM模型">
          <el-select v-model="agentForm.llm_uuid" placeholder="请选择LLM模型">
            <el-option 
              v-for="item in llmOptions" 
              :key="item.llm_uuid" 
              :label="item.name" 
              :value="item.llm_uuid" />
          </el-select>
        </el-form-item>
        <el-form-item label="系统提示词">
          <el-input v-model="agentForm.system_prompt" type="textarea" :rows="5" />
        </el-form-item>
        <el-form-item label="开场白">
          <el-input v-model="agentForm.opening_statement" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="图标">
          <el-upload
            class="avatar-uploader"
            action="/api/upload"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload">
            <img v-if="agentForm.icon" :src="agentForm.icon" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        
        <el-divider>高级配置</el-divider>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="知识库配置" name="knowledge">
            <el-form-item label="启用知识库">
              <el-switch v-model="agentForm.knowledge_config.enabled" />
            </el-form-item>
            <template v-if="agentForm.knowledge_config.enabled">
              <el-form-item label="知识库来源">
                <el-select v-model="agentForm.knowledge_config.source" placeholder="请选择知识库来源">
                  <el-option label="文件上传" value="file" />
                  <el-option label="网页抓取" value="web" />
                  <el-option label="API接入" value="api" />
                </el-select>
              </el-form-item>
            </template>
          </el-tab-pane>
          
          <el-tab-pane label="记忆配置" name="memory">
            <el-form-item label="启用长期记忆">
              <el-switch v-model="agentForm.memory_config.enabled" />
            </el-form-item>
            <template v-if="agentForm.memory_config.enabled">
              <el-form-item label="记忆长度">
                <el-input-number v-model="agentForm.memory_config.max_length" :min="1" :max="100" />
              </el-form-item>
            </template>
          </el-tab-pane>
          
          <el-tab-pane label="网络搜索配置" name="websearch">
            <el-form-item label="启用网络搜索">
              <el-switch v-model="agentForm.websearch_config.enabled" />
            </el-form-item>
            <template v-if="agentForm.websearch_config.enabled">
              <el-form-item label="搜索引擎">
                <el-select v-model="agentForm.websearch_config.engine" placeholder="请选择搜索引擎">
                  <el-option label="Google" value="google" />
                  <el-option label="Bing" value="bing" />
                  <el-option label="Baidu" value="baidu" />
                </el-select>
              </el-form-item>
            </template>
          </el-tab-pane>
          
          <el-tab-pane label="MCP配置" name="mcp">
            <el-form-item label="启用MCP">
              <el-switch v-model="agentForm.mcp_config.enabled" />
            </el-form-item>
            <template v-if="agentForm.mcp_config.enabled">
              <el-form-item label="MCP类型">
                <el-select v-model="agentForm.mcp_config.type" placeholder="请选择MCP类型">
                  <el-option label="基础MCP" value="basic" />
                  <el-option label="高级MCP" value="advanced" />
                </el-select>
              </el-form-item>
            </template>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAgentForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 智能体列表数据
const loading = ref(false)
const agentList = ref([])
const llmOptions = ref([])
const activeTab = ref('knowledge')

// 表单相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const agentForm = reactive({
  agent_uuid: '',
  llm_uuid: '',
  agent_name: '',
  description: '',
  icon: '',
  system_prompt: '你是一个有用的AI助手。',
  opening_statement: '你好！我是你的AI助手，有什么可以帮助你的吗？',
  knowledge_config: {
    enabled: false,
    source: 'file'
  },
  memory_config: {
    enabled: false,
    max_length: 10
  },
  websearch_config: {
    enabled: false,
    engine: 'google'
  },
  mcp_config: {
    enabled: false,
    type: 'basic'
  }
})

// 获取智能体列表
const fetchAgentList = async () => {
  loading.value = true
  try {
    // 模拟API调用
    setTimeout(() => {
      agentList.value = [
        {
          agent_uuid: 'agent-001',
          agent_name: '客服助手',
          llm_name: 'GPT-3.5-Turbo',
          llm_uuid: 'llm-001',
          description: '专业的客服智能体，可以回答产品相关问题',
          icon: 'https://example.com/avatar1.png'
        },
        {
          agent_uuid: 'agent-002',
          agent_name: '营销顾问',
          llm_name: 'Claude-2',
          llm_uuid: 'llm-002',
          description: '专业的营销顾问，可以提供营销策略建议',
          icon: 'https://example.com/avatar2.png'
        }
      ]
      loading.value = false
    }, 500)
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败')
    loading.value = false
  }
}

// 获取LLM模型选项
const fetchLLMOptions = async () => {
  try {
    // 模拟API调用
    setTimeout(() => {
      llmOptions.value = [
        {
          llm_uuid: 'llm-001',
          name: 'GPT-3.5-Turbo'
        },
        {
          llm_uuid: 'llm-002',
          name: 'Claude-2'
        }
      ]
    }, 500)
  } catch (error) {
    console.error('获取LLM模型选项失败:', error)
    ElMessage.error('获取LLM模型选项失败')
  }
}

// 创建智能体
const handleCreateAgent = () => {
  isEdit.value = false
  agentForm.agent_uuid = ''
  agentForm.llm_uuid = ''
  agentForm.agent_name = ''
  agentForm.description = ''
  agentForm.icon = ''
  agentForm.system_prompt = '你是一个有用的AI助手。'
  agentForm.opening_statement = '你好！我是你的AI助手，有什么可以帮助你的吗？'
  agentForm.knowledge_config.enabled = false
  agentForm.memory_config.enabled = false
  agentForm.websearch_config.enabled = false
  agentForm.mcp_config.enabled = false
  dialogVisible.value = true
}

// 编辑智能体
const handleEdit = (row) => {
  isEdit.value = true
  agentForm.agent_uuid = row.agent_uuid
  agentForm.llm_uuid = row.llm_uuid
  agentForm.agent_name = row.agent_name
  agentForm.description = row.description
  agentForm.icon = row.icon
  // 这里应该从API获取完整的智能体配置
  dialogVisible.value = true
}

// 删除智能体
const handleDelete = async (row