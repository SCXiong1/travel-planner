import { createRouter, createWebHistory } from "vue-router";
import { isLoggedIn } from "../api/client.js";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/trips",
    name: "TripList",
    component: () => import("../views/TripList.vue"),
  },
  {
    path: "/trips/:id",
    name: "TripDetail",
    component: () => import("../views/TripDetail.vue"),
  },
  {
    path: "/trips/:id/packing",
    name: "PackingList",
    component: () => import("../views/PackingList.vue"),
  },
  {
    path: "/trips/:id/settlement",
    name: "Settlement",
    component: () => import("../views/Settlement.vue"),
  },
  {
    path: "/trips/:id/recycle-bin",
    name: "RecycleBin",
    component: () => import("../views/RecycleBin.vue"),
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
