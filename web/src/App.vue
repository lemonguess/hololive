<template>
  <div class="app-container">
    <el-container>
      <el-aside width="200px">
        <el-menu
          router
          :default-active="$route.path"
          class="el-menu-vertical">
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/providers">
            <el-icon><Connection /></el-icon>
            <span>供应商管理</span>
          </el-menu-item>
          <el-menu-item index="/llm">
            <el-icon><Monitor /></el-icon>
            <span>LLM模型管理</span>
          </el-menu-item>
          <el-menu-item index="/agents">
            <el-icon><Avatar /></el-icon>
            <span>智能体管理</span>
          </el-menu-item>
          <el-menu-item index="/tts">
            <el-icon><Microphone /></el-icon>
            <span>TTS配置</span>
          </el-menu-item>
          <el-menu-item index="/avatar">
            <el-icon><User /></el-icon>
            <span>形象配置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-content">
            <h1>Hololive管理系统</h1>
            <div class="user-info">
              <el-dropdown>
                <span class="el-dropdown-link">
                  管理员
                  <el-icon class="el-icon--right">
                    <arrow-down />
                  </el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>个人信息</el-dropdown-item>
                    <el-dropdown-item>退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { HomeFilled, Connection, Monitor, Avatar, Microphone, User, ArrowDown } from '@element-plus/icons-vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  height: 100vh;
  width: 100%;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  border-bottom: 1px solid #eee;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.el-menu {
  border-right: none;
  height: 100%;
}

.el-menu-vertical {
  height: 100%;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}
</style>