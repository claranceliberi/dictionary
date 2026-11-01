import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import BrowseView from './views/BrowseView.vue'
import EntryView from './views/EntryView.vue'
import GuideView from './views/GuideView.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/browse/:letter', component: BrowseView },
    { path: '/search', component: BrowseView },
    { path: '/entry/:id', component: EntryView },
    { path: '/uko-wasoma', component: GuideView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

createApp(App).use(router).mount('#app')
