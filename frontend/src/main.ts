import { setupPwa } from "./services/pwa";
import { createApp } from "vue";
import App from "./App.vue";
import "./assets/style.css";
createApp(App).mount("#app");

setupPwa();
