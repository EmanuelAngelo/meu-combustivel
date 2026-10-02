import { inject, type InjectionKey } from "vue";
import type { useApplication } from "./useApplication";
export const appKey: InjectionKey<ReturnType<typeof useApplication>> =
  Symbol("application");
export function useAppContext() {
  const context = inject(appKey);
  if (!context) throw new Error("Application context is missing");
  return context;
}
