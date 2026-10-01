import {ref} from 'vue'
export const online=ref(navigator.onLine)
export const installPrompt=ref<any>(null)
export function setupPwa(){
 window.addEventListener('online',()=>online.value=true)
 window.addEventListener('offline',()=>online.value=false)
 window.addEventListener('beforeinstallprompt',(event:Event)=>{event.preventDefault();installPrompt.value=event})
 window.addEventListener('appinstalled',()=>installPrompt.value=null)
 if(import.meta.env.PROD&&'serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js').catch(()=>{})})}
}
export async function installApp(){if(!installPrompt.value)return;await installPrompt.value.prompt();await installPrompt.value.userChoice;installPrompt.value=null}
