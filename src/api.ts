import {ref} from 'vue'
export type Account={id:number,name:string,email:string}
export const isDemo=import.meta.env.VITE_API_MODE==='demo'
export const currentUser=ref<Account|null>(null)
export const passwordResetAvailable=ref(false)
const apiBase=(import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '')
let csrfToken=''
export class ApiError extends Error { constructor(message:string,public status=0){super(message)} }
function errorText(data:any):string {if(typeof data==='string')return data;if(Array.isArray(data))return data.map(errorText).join(' ');if(data&&typeof data==='object')return Object.values(data).map(errorText).join(' ');return 'Não foi possível concluir a operação.'}
export async function api<T=any>(path:string,method='GET',body?:unknown):Promise<T>{
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),15000)
 try{
  const response=await fetch(apiBase+'/'+path,{method,credentials:'include',cache:'no-store',signal:controller.signal,headers:{Accept:'application/json',...(body!==undefined?{'Content-Type':'application/json'}:{}),...(method!=='GET'?{'X-CSRFToken':csrfToken}:{})},body:body===undefined?undefined:JSON.stringify(body)})
  if(response.status!==204 && !response.headers.get('content-type')?.includes('application/json')) throw new ApiError('A API não retornou JSON. Confira a configuração de conexão com o servidor.', response.status)
  const data=response.status===204?null:await response.json().catch(()=>({detail:'O servidor retornou uma resposta inesperada.'}))
  if(!response.ok){if(response.status===403&&/credenciais.*não|Authentication credentials/i.test(errorText(data))){currentUser.value=null;window.dispatchEvent(new Event('session-expired'))}throw new ApiError(errorText(data),response.status)}
  if(data?.csrfToken)csrfToken=data.csrfToken
  return data as T
 }catch(e){if(e instanceof ApiError)throw e;throw new ApiError(navigator.onLine?'Não foi possível acessar o servidor. Tente novamente.':'Você está sem conexão. Seus campos continuam aqui; reconecte para salvar.')}finally{clearTimeout(timer)}
}
export async function restoreSession(){const data=await api('auth/session/');currentUser.value=data.user;passwordResetAvailable.value=data.passwordResetAvailable;return data}
export async function authenticateAccount(mode:'login'|'register',data:unknown){const result=await api('auth/'+mode+'/','POST',data);currentUser.value=result.user;passwordResetAvailable.value=result.passwordResetAvailable;return result}
export async function signOut(){await api('auth/logout/','POST',{});currentUser.value=null}
export function errorMessage(e:unknown){return e instanceof Error?e.message:'Não foi possível concluir a operação.'}
