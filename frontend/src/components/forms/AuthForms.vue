<script setup lang="ts">
import { ref } from "vue";
import {
  Droplet,
  ShieldCheck,
  Eye,
  EyeOff,
  ArrowLeft,
  CheckCircle2,
} from "lucide-vue-next";
import {
  api,
  type Account,
  authenticateAccount,
  errorMessage,
  passwordResetAvailable,
} from "../../services/api";
const emit = defineEmits<{ authenticated: [account: Account] }>();
const params = new URLSearchParams(location.search);
const mode = ref<"login" | "register" | "forgot" | "reset">(
  params.has("uid") && params.has("token") ? "reset" : "login",
);
const name = ref(""),
  email = ref(""),
  password = ref(""),
  confirm = ref(""),
  show = ref(false),
  busy = ref(false),
  error = ref(""),
  message = ref("");
function change(value: typeof mode.value) {
  mode.value = value;
  error.value = "";
  message.value = "";
  password.value = "";
  confirm.value = "";
}
async function submit() {
  if (busy.value) return;
  busy.value = true;
  error.value = "";
  message.value = "";
  try {
    if (
      (mode.value === "register" || mode.value === "reset") &&
      password.value !== confirm.value
    )
      throw new Error("As senhas precisam ser iguais.");
    if (mode.value === "forgot") {
      const r = await api("auth/password-reset/", "POST", {
        email: email.value,
      });
      message.value = r.detail;
    } else if (mode.value === "reset") {
      const r = await api("auth/password-confirm/", "POST", {
        uid: params.get("uid"),
        token: params.get("token"),
        password: password.value,
      });
      history.replaceState(null, "", location.pathname);
      change("login");
      message.value = r.detail;
    } else {
      const result = await authenticateAccount(mode.value, {
        name: name.value,
        email: email.value,
        password: password.value,
      });
      emit("authenticated", result.user);
    }
  } catch (e) {
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <main class="auth-layout">
    <section class="auth-story">
      <a class="brand auth-brand" href="/"
        ><span class="brand-icon"><Droplet :size="27" /></span
        ><span>meu<span class="brand-second">combustível.</span></span></a
      >
      <div>
        <span class="eyebrow">CADA LITRO CONTA</span>
        <h1>Seu caminho.<br />Suas contas<br />em dia.</h1>
        <p>
          Acompanhe seus abastecimentos e encontre os melhores preços para a
          próxima parada.
        </p>
      </div>
      <div class="auth-assurance">
        <ShieldCheck :size="25" />
        <p>
          Seus veículos e abastecimentos são privados. Você escolhe quais preços
          compartilhar.
        </p>
      </div>
    </section>
    <section class="auth-form-area">
      <div class="auth-form-card">
        <span class="eyebrow">MEU COMBUSTÍVEL</span>
        <h2>
          {{
            mode === "register"
              ? "Vamos começar?"
              : mode === "forgot"
                ? "Recuperar acesso"
                : mode === "reset"
                  ? "Escolha uma nova senha"
                  : "Bom ter você por aqui."
          }}
        </h2>
        <p>
          {{
            mode === "register"
              ? "Crie sua conta para cuidar de cada abastecimento."
              : mode === "login"
                ? "Entre para continuar de onde parou."
                : mode === "forgot"
                  ? "Vamos enviar as instruções para seu e-mail."
                  : "Use pelo menos 10 caracteres e evite senhas comuns."
          }}
        </p>
        <form @submit.prevent="submit">
          <label v-if="mode === 'register'" class="field"
            ><span>Seu nome</span
            ><input
              v-model="name"
              autocomplete="name"
              maxlength="150"
              required /></label
          ><label v-if="mode !== 'reset'" class="field"
            ><span>E-mail</span
            ><input
              v-model="email"
              type="email"
              autocomplete="email"
              maxlength="150"
              required
              placeholder="voce@exemplo.com" /></label
          ><label v-if="mode !== 'forgot'" class="field"
            ><span>Senha</span>
            <div class="password-field">
              <input
                v-model="password"
                :type="show ? 'text' : 'password'"
                :autocomplete="
                  mode === 'login' ? 'current-password' : 'new-password'
                "
                :minlength="mode === 'login' ? undefined : 10"
                maxlength="128"
                required
              /><button
                type="button"
                @click="show = !show"
                :aria-label="show ? 'Ocultar senha' : 'Mostrar senha'"
              >
                <component :is="show ? EyeOff : Eye" :size="19" />
              </button>
            </div>
            <small v-if="mode === 'register'"
              >Pelo menos 10 caracteres. Evite nomes e senhas comuns.</small
            ></label
          ><label v-if="mode === 'register' || mode === 'reset'" class="field"
            ><span>Confirme a senha</span
            ><input
              v-model="confirm"
              :type="show ? 'text' : 'password'"
              autocomplete="new-password"
              minlength="10"
              maxlength="128"
              required /></label
          ><button
            v-if="mode === 'login' && passwordResetAvailable"
            type="button"
            class="text-button forgot-link"
            @click="change('forgot')"
          >
            Esqueci minha senha
          </button>
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
          <div v-if="message" class="auth-success" role="status">
            <CheckCircle2 :size="20" />{{ message }}
          </div>
          <button class="primary-button wide" :disabled="busy">
            {{
              busy
                ? "Aguarde…"
                : mode === "login"
                  ? "Entrar na minha conta"
                  : mode === "register"
                    ? "Criar minha conta"
                    : mode === "forgot"
                      ? "Enviar instruções"
                      : "Salvar nova senha"
            }}
          </button>
        </form>
        <p v-if="mode === 'login'" class="auth-switch">
          Ainda não tem conta?
          <button class="text-button" @click="change('register')">
            Criar conta
          </button>
        </p>
        <p v-else class="auth-switch">
          <button class="text-button" @click="change('login')">
            <ArrowLeft :size="15" />Voltar para entrar
          </button>
        </p>
      </div>
    </section>
  </main>
</template>
