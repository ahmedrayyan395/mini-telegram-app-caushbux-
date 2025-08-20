import path from 'path';
import { defineConfig, loadEnv } from 'vite';
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
        define: {
            'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
            'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
        },
        resolve: {
            alias: {
                '@': path.resolve(__dirname, '.'),
            }
        },
        server: {
            allowedHosts: [
                'a9e0d6bd80a5.ngrok-free.app', // Add your ngrok host here
                'localhost', // You can also add localhost if needed
            ],
            // Optionally, you can add other server settings like port, cors, etc.
            port: 3000, // Change to your desired port
        }
    };
});