/**
import 'vite/modulepreload-polyfill'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
*/

import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { ObserveVisibility } from 'vue-observe-visibility';

import { createApp, defineComponent } from 'vue/dist/vue.esm-bundler.js';
import NotificationList from './components/NotificationList.vue';

const RootComponent = defineComponent({
  components: {
    'notification-list': NotificationList,
  },
});

const app = createApp(RootComponent);
app.directive('observe-visibility', {
  beforeMount: (el, binding, vnode) => {
    vnode.context = binding.instance;
    ObserveVisibility.bind(el, binding, vnode);
  },
  update: ObserveVisibility.update,
  unmounted: ObserveVisibility.unbind,
});

app.mount('#app');
