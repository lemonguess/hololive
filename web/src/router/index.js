import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/providers',
    name: 'Providers',
    component: () => import('../views/providers/ProvidersView.vue')
  },
  {
    path: '/llm',
    name: 'LLM',
    component: () => import('../views/llm/LLMView.vue')
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('../views/agents/AgentsView.vue')
  },
  {
    path: '/tts',
    name: 'TTS',
    component: () => import('../views/tts/TTSView.vue')
  },
  {
    path: '/avatar',
    name: 'Avatar',
    component: () => import('../views/avatar/AvatarView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router