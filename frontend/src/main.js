/**
import 'vite/modulepreload-polyfill'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
*/

import 'vite/modulepreload-polyfill'; // required for vite entrypoints

import { createApp, defineComponent } from 'vue/dist/vue.esm-bundler.js';
import HelloWorld from './components/HelloWorld.vue'

const RootComponent = defineComponent({
  components: {
    'hello-world': HelloWorld,
  },
});

const app = createApp(RootComponent);
app.mount('#app');
