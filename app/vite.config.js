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
        '^/api': {
          target: 'http://localhost:20090',
          rewrite: (path) => path.replace(/^\/api/, ''),
          changeOrigin: true,
          followRedirects: true,
          bypass: (req, res) => {
            if (req.url === '/api/manager') {
              res.writeHead(302, {
                Location: 'http://localhost:20090'
              })
              res.end()
            }
          },
        }
      }
    },
    base: env.VITE_BASE ?? "/"
  }
})
