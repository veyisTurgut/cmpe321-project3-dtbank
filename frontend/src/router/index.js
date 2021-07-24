import { createWebHistory, createRouter } from "vue-router";
import UserHome from "../pages/UserHome.vue"
import DBManagerGetHome from "../pages/DBManagerGetHome.vue"
import DBManagerCUDHome from "../pages/DBManagerCUDHome.vue"
import Login from "../pages/Login.vue"

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
  },
  {
    path: "/userhome",
    name: "UserHome",
    component: UserHome,
  },
  {
    path: "/dbhomeget",
    name: "DBHomeGet",
    component: DBManagerGetHome,
  }, 
  {
    path: "/dbhomecud",
    name: "DBHomeCud",
    component: DBManagerCUDHome,
  }, 
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;