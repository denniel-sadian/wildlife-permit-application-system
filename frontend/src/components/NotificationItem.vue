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
    <div>
        <i class="fa fa-info-circle info-icon"></i>
    </div>
    <div class="msg">
        <span class="notif-msg">{{ data.message }}</span>
        <span class="notif-date">{{ dateDisplay }}</span>
    </div>
</div>
</template>

<style scoped>
.notif-item {
    display: grid;
    margin: 0px 20px 20px 20px;
    border-radius: 12px;
    padding: 15px 20px 20px 20px;
    transition: 0.3s;
    background-color: #f3f3f3;
    grid-template-columns: auto 1fr;
}

.info-icon {
    color: #2196F3;
}


.notif-item .msg {
    display: flex;
    flex-direction: column;
    padding-left: 10px;
}

.unread {
    background-color: #ddffff;
}

.notif-item:hover {
    background-color: #87CEEB;
    cursor: pointer;
}

.notif-date {
    text-align: right;
    color: gray;
    font-size: 10px;
    margin-top: 10px;
}
</style>
