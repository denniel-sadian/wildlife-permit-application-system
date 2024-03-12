<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
    item: Object,
});

const data = ref({});

const dateDisplay = computed(() => {
    if (data) {
        const date = new Date(data.value.created_at);
        return date.toLocaleString();
    }
});

async function markRead() {
    if (!data.value.read) {
        await fetch(`/api/notifications/${data.value.id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({read: true})
        })
        .then(response => {
            return response.json();
        })
        .then((newData) => {
            data.value = newData;
        });
    }

    if (data.value.url) {
        window.location.href = data.value.url;
    }
}

onMounted(async () => {
    data.value = props.item;
});
</script>

<template>
<div class="notif-item" :class="{'unread': !data.read}" @click="markRead">
    <i class="fa fa-info-circle"></i>
    <span class="notif-msg">{{ data.message }}</span>
    <span class="notif-date">{{ dateDisplay }}</span>
</div>
</template>

<style scoped>
.notif-item {
    display: flex;
    flex-direction: column;
    margin: 0px 20px 10px 20px;
    border-radius: 12px;
    padding: 20px 10px 6px 10px;
    transition: 0.3s;
    background-color: #f3f3f3;
}

.unread {
    background-color: #ddffff;
}

.notif-item:hover {
    background-color: #87CEEB;
    cursor: pointer;
}

.notif-msg {
    margin-top: 8px;
}

.notif-date {
    text-align: right;
    color: gray;
    font-size: 10px;
}
</style>
