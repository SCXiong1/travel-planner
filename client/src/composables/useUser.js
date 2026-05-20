import { ref } from "vue";
import { getCurrentUser, setUser as saveUser } from "../api/client.js";

const current = ref(getCurrentUser());

export function useUser() {
  function login(user) {
    saveUser(user);
    current.value = user;
  }

  function logout() {
    saveUser("");
    current.value = "";
  }

  return { current, login, logout };
}
