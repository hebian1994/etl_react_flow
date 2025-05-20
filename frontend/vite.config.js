import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000, // 可根据需要更改端口
        proxy: {
            '/api': 'http://localhost:5000', // 假设你的 Flask 后端跑在 5000 端口
        },
    },
});
