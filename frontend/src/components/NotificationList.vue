<script setup>
import { ref, computed, onMounted } from 'vue';
import NotificationItem from './NotificationItem.vue';

const notifications = ref({});
const showNotifs = ref(false);

const unreadNotifCount = computed(() => {
    if (notifications.value.results) {
        return notifications.value.results.filter(n => n.read == false).length;
    }
    return 0;
});

async function getNotifs(link) {
    if (link == null) link = '/api/notifications/';
    const response = await fetch(link);
    return await response.json();
}

async function scrolledEnd(isVisible, entry) {
    if (!notifications.value.next) return;
    const data = await getNotifs(notifications.value.next);
    const newList = [...notifications.value.results, ...data.results];
    data.results = newList;
    notifications.value = data;
}

onMounted(async () => {
    const data = await getNotifs(null);
    notifications.value = data;
});
</script>

<template>
<div v-if="showNotifs" class="notification-cont">
  <div class="notification-panel">
    <button class="notif-close-btn w3-btn" @click="showNotifs = !showNotifs">
        <i class="fa fa-close"></i>
    </button>
    <h2>Notifications</h2>
    <div class="notif-list">
        <NotificationItem v-for="item in notifications.results" :key="item.id" :item="item">
        </NotificationItem>
        <p v-observe-visibility="scrolledEnd" class="end-spinner">
            <i v-if="notifications.next != null" class="fa fa-spinner w3-spin"></i>
            <span v-else>All caught up.</span>
        </p>
    </div>
  </div>
</div>

<div v-else class="notif-bell" @click="showNotifs = !showNotifs">
    <i class="fa fa-bell"></i>
    <span v-if="unreadNotifCount" class="unread-count">{{ unreadNotifCount }}</span>
</div>
</template>

<style scoped>
.notification-cont {
    position: fixed;
    display: flex;
    top: 0px;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.4);
    flex-direction: column;
    align-items: flex-end;
    box-sizing: border-box;
    padding: 20px;
}

.notification-cont h2 {
    font-size: 30px;
    padding: 0px 20px;
}

.notification-panel {
    background-color: white;
    width: 35%;
    height: 100%;
    border-radius: 12px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    position: relative;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    padding-bottom: 20px;
}

.notif-close-btn {
    position: absolute;
    top: 0px;
    right: 0px;
    width: 35px;
    height: 35px;
    border-radius: 12px;
    border: none;
    background-color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.notif-list {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    box-sizing: border-box;
}

.notif-bell {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #009688;
    color: #fff;
    width: 55px;
    height: 55px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    border-radius: 100%;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
.unread-count {
    position: absolute;
    top: 0px;
    right: -5px;
    background-color: #f44336;
    color: white;
    font-size: 12px;
    width: 20px;
    height: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 100%;
}

.end-spinner {
    text-align: center;
}

@media only screen and (max-width: 1000px) {
    .notification-panel {
        width: 100%
    }
}
</style>
