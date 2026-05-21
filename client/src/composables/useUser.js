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

  function switchUser() {
    const next = current.value === "sd" ? "sg" : "sd";
    saveUser(next);
    current.value = next;
    return next;
  }

  return { current, login, logout, switchUser };
}
