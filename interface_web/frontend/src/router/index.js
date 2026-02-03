import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import OperadoraView from "@/views/OperadoraView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/operadoras/:cnpj", name: "operadora", component: OperadoraView }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
