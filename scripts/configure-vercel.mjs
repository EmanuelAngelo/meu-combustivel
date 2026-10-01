import { readFileSync, writeFileSync } from 'node:fs'
const file = new URL('../vercel.json', import.meta.url)
try {
 const url = new URL(process.argv[2])
 if (url.protocol !== 'https:' || url.username || url.password || url.pathname !== '/' || url.search || url.hash) throw new Error()
 const config = JSON.parse(readFileSync(file, 'utf8'))
 config.rewrites[0].destination = `${url.origin}/api/:path*`
 writeFileSync(file, JSON.stringify(config, null, 2) + '\n')
 console.log('vercel.json atualizado. Envie esse arquivo ao repositório antes do deploy.')
} catch {
 console.error('Uso: npm run configure:vercel -- https://SEU-USUARIO.pythonanywhere.com')
 process.exit(1)
}
