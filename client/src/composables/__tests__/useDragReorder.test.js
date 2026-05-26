import { describe, it, expect, vi } from "vitest";
import { ref, nextTick } from "vue";
import { useDragReorder } from "../useDragReorder.js";

describe("useDragReorder", () => {
  const makePointerEvent = (y = 0) =>
    new PointerEvent("pointermove", { clientX: 0, clientY: y });

  function setup(items, enabled) {
    const itemList = items || [{ id: "a" }, { id: "b" }, { id: "c" }];
    const onReorder = vi.fn();
    const onClick = vi.fn();
    const itemsRef = ref([...itemList]);
    const comp = useDragReorder({
      items: itemsRef,
      onReorder,
      onClick,
      ...(enabled !== undefined && { enabled }),
    });

    // 注册 mock DOM 元素
    itemsRef.value.forEach((_, i) => {
      const el = document.createElement("div");
      el.getBoundingClientRect = () => ({
        top: i * 50,
        bottom: i * 50 + 50,
        height: 50,
        left: 0,
        right: 100,
        width: 100,
        x: 0,
        y: i * 50,
        toJSON: () => {},
      });
      comp.setCardRef(i, el);
    });

    return { comp, onReorder, onClick, itemsRef };
  }

  // Tracer bullet: 拖拽开始时设置 dragging 和 dragIndex
  it("onDragStart sets dragging and dragIndex", () => {
    const { comp } = setup();
    const el = document.createElement("div");
    // 用 setPointerCapture 的 mock
    el.setPointerCapture = vi.fn();

    const ev = new PointerEvent("pointerdown", {
      pointerId: 1,
      clientX: 0,
      clientY: 50,
    });
    Object.defineProperty(ev, "currentTarget", { value: el, writable: false });

    comp.onDragStart(1, ev);

    expect(comp.dragging.value).toBe(true);
    expect(comp.dragIndex.value).toBe(1);
  });

  it("onDragMove computes dropBefore from pointer Y", () => {
    const { comp } = setup();

    // 先开始拖拽
    const el = document.createElement("div");
    el.setPointerCapture = vi.fn();
    const startEv = new PointerEvent("pointerdown", { pointerId: 1 });
    Object.defineProperty(startEv, "currentTarget", { value: el, writable: false });
    comp.onDragStart(1, startEv);

    // 指针移到第 0 个元素上方 (y=10, midpoint=25 → 应插入位置0)
    comp.onDragMove(makePointerEvent(10));
    expect(comp.dropBefore.value).toBe(0);

    // 指针移到最后面 (y=200, 超过所有元素 → 应插入位置3)
    comp.onDragMove(makePointerEvent(200));
    expect(comp.dropBefore.value).toBe(3);
  });

  it("onDragEnd calls onReorder with correct orders when position changed", async () => {
    const { comp, onReorder } = setup();

    const el = document.createElement("div");
    el.setPointerCapture = vi.fn();
    const startEv = new PointerEvent("pointerdown", { pointerId: 1 });
    Object.defineProperty(startEv, "currentTarget", { value: el, writable: false });
    comp.onDragStart(0, startEv);

    // 从索引0拖到索引2后面 (y > 125 = item2 midpoint → dropBefore=3)
    comp.onDragMove(makePointerEvent(160));
    comp.onDragEnd();

    expect(onReorder).toHaveBeenCalledTimes(1);
    const orders = onReorder.mock.calls[0][0];
    // 原 ["a","b","c"]，a 从 0 移到 2 后面 → ["b","c","a"]
    expect(orders).toEqual([
      { id: "b", sort_order: 0 },
      { id: "c", sort_order: 1 },
      { id: "a", sort_order: 2 },
    ]);
  });

  it("onDragEnd does NOT call onReorder when position unchanged", () => {
    const { comp, onReorder } = setup();

    const el = document.createElement("div");
    el.setPointerCapture = vi.fn();
    const startEv = new PointerEvent("pointerdown", { pointerId: 1 });
    Object.defineProperty(startEv, "currentTarget", { value: el, writable: false });
    comp.onDragStart(1, startEv);

    // dropBefore === dragIndex (同位置)
    comp.onDragMove(makePointerEvent(70)); // item 1 midpoint=75, y=70 → dropBefore=1
    comp.onDragEnd();

    expect(onReorder).not.toHaveBeenCalled();
  });

  it("onCardClick suppresses click when drag just ended", async () => {
    const { comp, onClick } = setup();

    const el = document.createElement("div");
    el.setPointerCapture = vi.fn();
    const startEv = new PointerEvent("pointerdown", { pointerId: 1 });
    Object.defineProperty(startEv, "currentTarget", { value: el, writable: false });
    comp.onDragStart(0, startEv);
    comp.onDragEnd();

    // nextTick 之前 dragJustEnded=true, click 应被抑制
    comp.onCardClick({ id: "a" });
    expect(onClick).not.toHaveBeenCalled();

    await nextTick();
    // nextTick 之后 dragJustEnded=false, click 应正常
    comp.onCardClick({ id: "a" });
    expect(onClick).toHaveBeenCalledWith({ id: "a" });
  });

  it("disabled composable prevents drag start", () => {
    const enabled = ref(false);
    const { comp } = setup(undefined, enabled);

    const el = document.createElement("div");
    const startEv = new PointerEvent("pointerdown", { pointerId: 1 });
    Object.defineProperty(startEv, "currentTarget", { value: el, writable: false });
    comp.onDragStart(0, startEv);

    expect(comp.dragging.value).toBe(false);
    expect(comp.dragIndex.value).toBe(-1);
  });
});
