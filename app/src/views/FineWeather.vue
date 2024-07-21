<template>
  <main class="pa-4 dark:bg-#131130">
    <div class="h-100vh w-100vw dots fixed pointer-events-none" :class="{ 'dark': isDark }"></div>
    <div class="
      columns-1 sm:columns-2 md:columns-3 xl:columns-4 2xl:columns-5
      gap-x-4
    ">
      <div class="
        bg-#4c1d9525 backdrop-blur-2 saturate-120%
        dark:bg-violet-950 dark:c-gray-200 break-inside-avoid
        rd-2 pa-4 box-border mb-4 c-slate-800 text-justify lh-6 tracking-.1 text-0px
      " :class="{ 'flex items-center justify-between': folded }">
        <template v-if="!folded">
          <div class="text-sm">{{ INTRO }}</div>
        </template>
        <strong class="text-1rem" v-else>{{ TITLE }}</strong>
        <div class="
          backdrop-blur-2 saturate-120% bg-#4c1d9525 pa-1 rd-50% cursor-pointer
          hover:bg-#4c1d9545 active:bg-#4c1d9562
          dark:bg-violet-900 dark:c-gray-200 dark:hover:bg-violet-800 dark:active:bg-violet-700
        " :class="{
          'absolute bottom-2 right-2': !folded
        }" @click="folded = !folded">
          <div class="text-xl" :class="folded ? 'i-mdi-chevron-down' : 'i-mdi-chevron-up'"></div>
        </div>
      </div>
      <ImageCard class="mb-4" v-for="img, index in images" :key="index" v-bind="img"
        @click="openDetail(index)" />
    </div>
    <div class="flex my-18 items-center flex-col select-none text-xs">
      <div class="text-gray-400 mb-3 mt-2.5">
        {{ images.length }}<span class="mx-.5">/</span>{{ totalImages }}
      </div>
      <div v-if="loadingImages" class="flex items-center">
        <i class="
          i-mdi-loading animate-iteration-infinite block
          animate-spin c-gray-600 dark:c-gray-200
        " />
      </div>
      <div class="
        c-gray-600 dark:c-gray-200 cursor-pointer
        rd-2 py-1 px-2 simple-btn
      " @click="loadMore" v-else-if="currPage <= totalPages">
        More
      </div>
      <div class="c-gray-600 dark:c-gray-200 py-1" v-else>
        No More
      </div>
    </div>
    <footer class="flex flex-col items-center">
      <div class="text-xl c-slate-800 flex items-center">
        <div class="
          backdrop-blur-2 saturate-120%
          pa-1 rd-50% mr-2 cursor-pointer
          simple-btn
        " @click="isDark = !isDark">
          <div class="i-mdi-white-balance-sunny"></div>
        </div>
        <div class="
          backdrop-blur-2 saturate-120%
          pa-1 rd-50% cursor-pointer
          simple-btn
        " @click="jumpTo('https://github.com/codekitchen-community/fine-weather')">
          <div class="i-mdi-github"></div>
        </div>
      </div>

      <div class="text-xs c-gray-600 dark:c-gray-200 mt-3">
        <div class="text-center">
          <span>&copy; {{ new Date().getFullYear() }}</span>
          <span class="
            ml-2 inline-flex c-gray-600 items-center cursor-pointer b-1 b-solid b-transparent
            hover:b-b-gray-600
            dark:c-gray-200 dark:hover:b-b-gray-200
          " @click="jumpTo('https://codekitchen.community/')">
            <span>CodeKitchen Community</span>
            <i class="i-mdi-open-in-new ml-1"></i>
          </span>
        </div>
        <div class="text-gray-400 mt-1">Last updated at {{ lastUpdatedAt }}
        </div>
      </div>
    </footer>
    <ImageDetail v-model="imageDetailModel" v-bind="{ ...imageDetails, total: totalImages }"
      @lastImage="openDetail(imageDetails.current - 1)"
      @nextImage="openDetail(imageDetails.current + 1)" />
    <div class="
      fixed h-100vh w-100vw flex items-center justify-center top-0 left-0
      bg-[rgba(47,14,59,0.62)] backdrop-blur-20 saturate-120
    " v-if="!images.length">
      <i class="
        i-mdi-loading animate-iteration-infinite c-white block
        text-3xl lg:text-4xl animate-spin
      " />
    </div>
  </main>
</template>

<script setup>
import {
  onMounted, reactive, ref, watchEffect,
} from 'vue'
import { useDark, useEventListener } from '@vueuse/core'
import ImageCard from '@/components/ImageCard.vue'
import ImageDetail from '@/components/ImageDetail.vue'

const PAGE_SIZE = 20
const TITLE = '「Fine Weather」'
const INTRO = `Fine Weather is a photo album application based on Vue and BootstrapFlask, which is built to collect ${TITLE} moments of life`

const isDark = useDark()
const imageDetailModel = ref(false)
const loadingImages = ref(false)
const folded = ref(false)
const isReady = ref(false)
const loaded = ref(0)
const currPage = ref(1)
const totalImages = ref(0)
const totalPages = ref(0)
const lastUpdatedAt = ref("Thu, 01 Apr 2010 00:00:00 GMT")
const imageDetails = reactive({
  imgMeta: {
    blurhash: '',
    created_at: '',
    description: '',
    height: '',
    position: '',
    time: '',
    title: '',
    uri: '',
    width: ''
  },
  current: 0,
})
const images = ref([])

function jumpTo(url) {
  const a = document.createElement('a')
  a.href = url
  a.target = '_blank'
  a.click()
}

async function openDetail(index) {
  if (index >= images.value.length) {
    await loadMore()
  }
  imageDetails.imgMeta = images.value[index]
  imageDetails.current = index
  imageDetailModel.value = true
}

function keypressListener(ev) {
  if (imageDetailModel.value) {
    if (ev.key === 'Escape') {
      imageDetailModel.value = false
    } else if (ev.key === 'ArrowLeft' && imageDetails.current > 0) {
      openDetail(imageDetails.current - 1)
    } else if (ev.key === 'ArrowRight' && imageDetails.current < totalImages.value - 1) {
      openDetail(imageDetails.current + 1)
    }
  }
}

async function loadMore() {
  loadingImages.value = true
  const resp = await fetch(`${import.meta.env.VITE_IMG_FETCH_BASE}/images?page_size=${PAGE_SIZE}&page=${currPage.value}`)
  if (resp.status === 200) {
    const imagesResult = await resp.json()
    currPage.value += 1
    totalImages.value = imagesResult.total
    totalPages.value = imagesResult.pages

    images.value.push(...imagesResult.images)
    imagesResult.images.forEach(img => {
      if (new Date(img.updated_at) > new Date(lastUpdatedAt.value)) {
        lastUpdatedAt.value = img.updated_at
      }
    })
  }
  loadingImages.value = false
}

onMounted(() => {
  useEventListener(document, 'keydown', keypressListener)
  loadMore()
  isReady.value = true
})

watchEffect(() => {
  if (imageDetailModel.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = 'auto'
  }
})
</script>

<style scoped>
.simple-btn {
  --at-apply: hover:bg-#4c1d9545 active:bg-#4c1d9562 bg-#4c1d9525;
  --at-apply: dark:bg-violet-900 dark:c-gray-200 dark:hover:bg-violet-800 dark:active:bg-violet-700;
}

.dots {
  background: url("data:image/svg+xml;utf8, <svg width='16' height='16' fill='none' xmlns='http://www.w3.org/2000/svg'><rect fill='rgba(25, 33, 38, 0.2)' x='7' y='7' width='2' height='2'></rect></svg>") fixed;
}

.dots.dark {
  background: url("data:image/svg+xml;utf8, <svg width='16' height='16' fill='none' xmlns='http://www.w3.org/2000/svg'><rect fill='rgba(255, 255, 255, 0.17)' x='7' y='7' width='2' height='2'></rect></svg>") fixed;
}
</style>
