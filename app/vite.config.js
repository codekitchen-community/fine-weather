import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import { presetUno, presetIcons } from 'unocss'
import { resolve } from 'path'
import transformerDirectives from '@unocss/transformer-directives'
import { loadEnv } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    plugins: [vue(), UnoCSS({
      presets: [presetIcons(), presetUno()],
      transformers: [transformerDirectives()],
    })],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      proxy: {
        '^/manager': {
          target: 'http://localhost:20099',
          changeOrigin: true
        }
      }
    },
    base: env.VITE_BASE ?? "/"
  }
})
