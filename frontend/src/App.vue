<script setup lang="ts">
import { provide } from "vue";
import { useApplication } from "./composables/useApplication";
import { appKey } from "./composables/appContext";
import AuthScreen from "./components/forms/AuthForms.vue";
import {
  Droplet,
  Fuel,
  LayoutDashboard,
  History,
  MapPin,
  Car,
  Plus,
  ChevronRight,
  ChevronDown,
  ArrowUpRight,
  Check,
  CheckCheck,
  ShieldCheck,
  Info,
  Wallet,
  CalendarDays,
  Gauge,
  Bike,
  Search,
  X,
  SlidersHorizontal,
  Navigation,
  Wind,
  CheckCircle2,
  AlertTriangle,
  ReceiptText,
  Trash2,
  Star,
  Menu,
  Globe,
  Download,
  RotateCcw,
} from "lucide-vue-next";
const application = useApplication();
provide(appKey, application);
const {
  modalOpen,
  isDemo,
  currentUser,
  online,
  installPrompt,
  installApp,
  nav,
  page,
  mobileMenu,
  vehicles,
  stations,
  booting,
  bootError,
  toast,
  go,
  modal,
  modalType,
  closeModal,
  startAccount,
  enterAccount,
  logoutAccount,
} = application;
import AbastecimentoView from "./views/AbastecimentoView.vue";
import VisaoGeralView from "./views/VisaoGeralView.vue";
import HistoricoView from "./views/HistoricoView.vue";
import VeiculosView from "./views/VeiculosView.vue";
import PostosView from "./views/PostosView.vue";
import VeiculoForms from "./components/forms/VeiculoForms.vue";
import PostoForms from "./components/forms/PostoForms.vue";
import RelatoForms from "./components/forms/RelatoForms.vue";
import AbastecimentoExibicao from "./components/exibicao/AbastecimentoExibicao.vue";
</script>
<template>
  <div v-if="booting" class="boot-screen" role="status">
    <Droplet :size="36" />
    <h1>Meu Combustível</h1>
    <p>Conectando à sua conta…</p>
  </div>
  <div v-else-if="bootError" class="boot-screen">
    <AlertTriangle :size="36" />
    <h1>Não foi possível conectar</h1>
    <p>{{ bootError }}</p>
    <button class="primary-button" @click="startAccount">
      Tentar novamente
    </button>
  </div>
  <AuthScreen
    v-else-if="!isDemo && !currentUser"
    @authenticated="enterAccount"
  />
  <div v-else class="app-shell">
    <aside class="sidebar" :class="{ open: mobileMenu }">
      <a href="#" class="brand" @click.prevent="go('home')"
        ><span class="brand-icon"
          ><Droplet :size="25" :stroke-width="2.3" /></span
        ><span
          >meu<span class="brand-second"
            >combustível<span class="brand-dot">.</span></span
          ></span
        ></a
      >
      <div class="sidebar-label">SEU DIA A DIA</div>
      <nav aria-label="Navegação principal">
        <button
          v-for="item in nav"
          :key="item.id"
          :class="['nav-item', { active: page === item.id }]"
          @click="go(item.id)"
          :aria-current="page === item.id ? 'page' : undefined"
        >
          <component :is="item.icon" :size="20" /><span>{{ item.label }}</span
          ><span v-if="item.id === 'fill'" class="nav-plus">+</span>
        </button>
      </nav>
      <div class="sidebar-bottom">
        <div class="private-note">
          <ShieldCheck :size="22" />
          <div>
            <strong>Seu histórico é só seu</strong>
            <p>Você escolhe os preços que compartilha.</p>
          </div>
        </div>
        <div class="preview-profile">
          <div class="avatar">MC</div>
          <div>
            <strong>{{
              isDemo ? "Modo demonstração" : currentUser?.name
            }}</strong
            ><span v-if="isDemo">Explore o Meu Combustível</span
            ><button v-else class="text-button" @click="logoutAccount">
              Sair da conta
            </button>
          </div>
        </div>
      </div>
    </aside>
    <button
      v-if="mobileMenu"
      class="menu-backdrop"
      @click="mobileMenu = false"
      aria-label="Fechar menu"
    ></button>
    <div class="workspace">
      <header class="topbar">
        <div class="breadcrumbs">
          <button
            class="mobile-menu icon-button"
            @click="mobileMenu = !mobileMenu"
            aria-label="Abrir menu"
          >
            <Menu :size="22" /></button
          ><span>Meu Combustível</span><ChevronRight :size="14" /><strong>{{
            nav.find((n) => n.id === page)?.label
          }}</strong>
        </div>
        <div class="location">
          <button
            v-if="installPrompt"
            class="text-button install-button"
            @click="installApp"
          >
            <Download :size="16" />Instalar app</button
          ><MapPin :size="16" /><span>São Luís, MA</span
          ><span class="country">BR</span>
        </div>
      </header>
      <div v-if="isDemo" class="demo-banner">
        <span class="demo-badge">PRÉVIA</span
        ><span
          >Dados de exemplo. Suas alterações ficam apenas nesta sessão.</span
        >
      </div>
      <div v-if="!online" class="offline-banner">
        <Info :size="17" />Sem conexão. Seus campos permanecem nesta tela.
        Reconecte para salvar.
      </div>
      <main>
        <Transition name="page" mode="out-in">
          <div :key="page">
            <AbastecimentoView v-if="page === 'fill'" />

            <VisaoGeralView v-else-if="page === 'home'" />

            <HistoricoView v-else-if="page === 'history'" />

            <VeiculosView v-else-if="page === 'vehicles'" />

            <PostosView v-else-if="page === 'stations'" />
          </div>
        </Transition>
        <footer class="app-footer">
          <span>Meu Combustível<span class="brand-dot">.</span></span
          ><span>Mais clareza a cada abastecimento.</span>
        </footer>
      </main>
    </div>
    <nav class="bottom-nav" aria-label="Navegação no celular">
      <button
        v-for="item in nav"
        :key="item.id"
        :class="{ active: page === item.id }"
        @click="go(item.id)"
        :aria-current="page === item.id ? 'page' : undefined"
      >
        <component :is="item.icon" :size="21" /><span>{{
          item.id === "home"
            ? "Início"
            : item.id === "stations"
              ? "Postos"
              : item.id === "vehicles"
                ? "Veículos"
                : item.label
        }}</span>
      </button>
    </nav>
    <Transition name="toast"
      ><div v-if="toast" class="toast" role="status">
        <CheckCircle2 :size="21" /><span>{{ toast }}</span
        ><button @click="toast = ''" aria-label="Fechar aviso">
          <X :size="17" />
        </button></div
    ></Transition>
    <dialog
      ref="modal"
      class="modal"
      @cancel.prevent="closeModal"
      @click="$event.target === modal && closeModal()"
    >
      <div v-if="modalOpen" class="modal-content">
        <button
          class="modal-close icon-button"
          @click="closeModal"
          aria-label="Fechar janela"
        >
          <X :size="21" />
        </button>
        <VeiculoForms v-if="modalType === 'vehicle'" />
        <PostoForms v-else-if="modalType === 'station'" />
        <AbastecimentoExibicao v-else-if="modalType === 'fillDetail'" />
        <RelatoForms v-else-if="modalType === 'report'" />
      </div>
    </dialog>
  </div>
</template>
