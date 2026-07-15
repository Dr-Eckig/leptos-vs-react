import { useEffect, useRef } from "react";

export function useClickOutside<T extends HTMLElement>(onClickOutside: () => void) {
  const elementRef = useRef<T>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        elementRef.current &&
        !elementRef.current.contains(event.target as Node)
      ) {
        onClickOutside();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClickOutside]);

  return elementRef;
}
