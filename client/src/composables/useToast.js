import { ref } from "vue";

const message = ref("");
const visible = ref(false);
const type = ref("error"); // "error" | "info"
let timer = null;

export function useToast() {
  function show(msg, opts = {}) {
    if (timer) clearTimeout(timer);
    message.value = msg;
    type.value = opts.type || "error";
    visible.value = true;
    timer = setTimeout(() => {
      visible.value = false;
    }, opts.duration || 3000);
  }

  return { message, visible, type, show };
}
