<template>
  <div class="
    cursor-pointer relative overflow-hidden rd-2 transition-170
    hover:scale-103
  " ref="containerRef">
    <Suspense>
      <template #default>
        <ImageAsync :src="imgSrc" class="
            w-100% block  dark:bg-[rgba(0,0,0,.2)] bg-[rgba(0,0,0,.1)]
            backdrop-blur-4 saturate-120" :style="{ minHeight: minImageHeight + 'px' }" />
      </template>
      <template #fallback>
        <canvas class="w-100% rd-2 block" ref="skeletonRef" width="32" height="32"></canvas>
      </template>
    </Suspense>
    <div class="
      absolute top-0 left-0 w-100% h-100% box-border flex items-end justify-start
      pa-4 opacity-0 hover:opacity-100 transition-170 mask
    ">
      <div class="c-white overflow-hidden">
        <div class="text-xl fw-bold">{{ title }}</div>
        <div class="text-sm flex mt-2" v-if="position || time">
          <div v-if="position" class="flex items-center mr-2">
            <i class="i-mdi-map-marker mr-1"></i>
            {{ position }}
          </div>
          <div v-if="time" class="flex items-center">
            <i class="i-mdi-clock mr-1"></i>
            {{ time }}
          </div>
        </div>
        <div class="text-sm text-truncate mt-2" v-if="description" :title="description">{{
          description
        }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { decode } from 'blurhash'
import ImageAsync from './ImageAsync.vue'

const props = defineProps({
  thumbnail_uri: String,
  title: {
    type: String,
    default: '无题',
  },
  position: String,
  time: String,
  description: String,
  blurhash: String,
  height: Number,
  width: Number
})
const skeletonRef = ref(null)
const containerRef = ref()

const imgSrc = computed(
  () => `${import.meta.env.VITE_IMG_FETCH_BASE}/${props.thumbnail_uri}`,
)
const minImageHeight = computed(
  () => Math.floor(
    (containerRef.value?.offsetWidth || 0) * (props.height / props.width),
  ),
)

onMounted(() => {
  skeletonRef.value.height = Math.floor((props.height / props.width) * 32)

  const pixels = decode(props.blurhash, 32, 32)
  const ctx = skeletonRef.value.getContext('2d')
  const imageData = ctx.createImageData(32, 32)
  imageData.data.set(pixels)
  ctx.putImageData(imageData, 0, 0)
})
</script>

<style scoped>
.mask {
  background: radial-gradient(rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.5) 100%),
    radial-gradient(rgba(0, 0, 0, 0) 33%, rgba(0, 0, 0, 0.3) 166%);
}
</style>
