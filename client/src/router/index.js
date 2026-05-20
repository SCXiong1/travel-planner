import { createRouter, createWebHistory } from "vue-router";
import { isLoggedIn } from "../api/client.js";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../components/Login.vue"),
  },
  {
    path: "/trips",
    name: "TripList",
    component: () => import("../components/TripList.vue"),
  },
  {
    path: "/trips/:id",
    name: "TripDetail",
    component: () => import("../components/TripDetail.vue"),
  },
  {
    path: "/trips/:id/packing",
    name: "PackingList",
    component: () => import("../components/PackingList.vue"),
  },
  {
    path: "/trips/:id/settlement",
    name: "Settlement",
    component: () => import("../components/Settlement.vue"),
  },
  {
    path: "/trips/:id/recycle-bin",
    name: "RecycleBin",
    component: () => import("../components/RecycleBin.vue"),
  },
  {
    path: "/",
    redirect: () => {
      return isLoggedIn() ? "/trips" : "/login";
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.name !== "Login" && !isLoggedIn()) {
    return "/login";
  }
});

export default router;
