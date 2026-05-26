import { ref, nextTick } from "vue";

export function useDragReorder({ items, onReorder, onClick, enabled = ref(true) }) {
  const cardRefs = {};
  const dragIndex = ref(-1);
  let dragGripEl = null;
  const dropBefore = ref(-1);
  const dragging = ref(false);
  const dragJustEnded = ref(false);

  function setCardRef(idx, el) {
    if (el) cardRefs[idx] = el;
  }

  function onDragStart(idx, event) {
    if (!enabled.value) return;
    dragIndex.value = idx;
    dragging.value = true;
    dragGripEl = event.currentTarget;
    dragGripEl.setPointerCapture(event.pointerId);
    dragGripEl.addEventListener("pointermove", onDragMove);
    dragGripEl.addEventListener("pointerup", onDragEnd);
    dragGripEl.addEventListener("pointercancel", onDragEnd);
  }

  function onDragMove(event) {
    const y = event.clientY;
    let ins = items.value.length;
    for (let i = 0; i < items.value.length; i++) {
      const rect = cardRefs[i]?.getBoundingClientRect();
      if (rect && y < rect.top + rect.height / 2) {
        ins = i;
        break;
      }
    }
    dropBefore.value = ins;
  }

  function onDragEnd() {
    if (dragGripEl) {
      dragGripEl.removeEventListener("pointermove", onDragMove);
      dragGripEl.removeEventListener("pointerup", onDragEnd);
      dragGripEl.removeEventListener("pointercancel", onDragEnd);
      dragGripEl = null;
    }

    if (
      dropBefore.value !== -1 &&
      dropBefore.value !== dragIndex.value &&
      dropBefore.value !== dragIndex.value + 1
    ) {
      const arr = [...items.value];
      const [moved] = arr.splice(dragIndex.value, 1);
      const newIdx =
        dropBefore.value < dragIndex.value
          ? dropBefore.value
          : dropBefore.value - 1;
      arr.splice(newIdx, 0, moved);
      const orders = arr.map((item, i) => ({ id: item.id, sort_order: i }));
      onReorder(orders);
    }

    dragIndex.value = -1;
    dropBefore.value = -1;
    dragging.value = false;
    dragJustEnded.value = true;
    nextTick(() => {
      dragJustEnded.value = false;
    });
  }

  function onCardClick(item) {
    if (dragJustEnded.value) return;
    onClick(item);
  }

  return {
    setCardRef,
    onDragStart,
    onDragMove,
    onDragEnd,
    onCardClick,
    dragging,
    dragJustEnded,
    dropBefore,
    dragIndex,
  };
}
