<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1>欢迎使用Hololive管理系统</h1>
      <p>这是一个智能体、TTS和形象配置的综合管理平台</p>
    </div>
    
    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>供应商管理</span>
            </div>
          </template>
          <div class="card-content">
            <p>管理AI模型供应商，配置API密钥</p>
            <el-button type="primary" @click="$router.push('/providers')">进入管理</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>LLM模型管理</span>
            </div>
          </template>
          <div class="card-content">
            <p>配置和管理大语言模型参数</p>
            <el-button type="primary" @click="$router.push('/llm')">进入管理</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Avatar /></el-icon>
              <span>智能体管理</span>
            </div>
          </template>
          <div class="card-content">
            <p>创建和配置AI智能体，设置系统提示词</p>
            <el-button type="primary" @click="$router.push('/agents')">进入管理</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Microphone /></el-icon>
              <span>TTS配置</span>
            </div>
          </template>
          <div class="card-content">
            <p>配置语音合成参数，管理音色和情绪</p>
            <el-button type="primary" @click="$router.push('/tts')">进入管理</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>形象配置</span>
            </div>
          </template>
          <div class="card-content">
            <p>管理虚拟形象，配置动作和表情</p>
            <el-button type="primary" @click="$router.push('/avatar')">进入管理</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </div>
          </template>
          <div class="card-content">
            <p>配置系统参数和用户信息</p>
            <el-button type="primary">进入设置</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <div class="system-info">
      <h3>系统信息</h3>
      <p>版本: v0.1.0</p>
      <p>服务状态: <el-tag type="success">运行中</el-tag></p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Connection, Monitor, Avatar, Microphone, User, Setting } from '@element-plus/icons-vue'

onMounted(() => {
  // 可以在这里加载系统状态信息
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-section h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 16px;
  color: #606266;
}

.feature-cards {
  margin-bottom: 20px;
}

.feature-card {
  height: 100%;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 18px;
}

.card-header .el-icon {
  margin-right: 10px;
  font-size: 20px;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100px;
}

.card-content p {
  margin-bottom: 15px;
  color: #606266;
}

.system-info {
  margin-top: 30px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.system-info h3 {
  margin-bottom: 10px;
  font-size: 16px;
  color: #303133;
}

.system-info p {
  margin: 5px 0;
  color: #606266;
}
</style>