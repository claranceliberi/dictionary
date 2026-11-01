import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import BrowseView from './views/BrowseView.vue'
import EntryView from './views/EntryView.vue'
import GuideView from './views/GuideView.vue'
import './style.css'
import { trackRequests } from './loading.js'

trackRequests()

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/browse/:letter', component: BrowseView },
    { path: '/search', component: BrowseView },
    // /ijambo/<id>-<slug>, e.g. /ijambo/1158-mubitsi; the number identifies the word
    { path: '/ijambo/:slug', component: EntryView },
    { path: '/entry/:id', redirect: (to) => `/ijambo/${to.params.id}` },
    { path: '/uko-wasoma', component: GuideView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

createApp(App).use(router).mount('#app')
