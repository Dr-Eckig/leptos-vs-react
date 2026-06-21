import { useEffect, useRef, type ReactNode } from "react";
import { type Alignment, alignmentClasses } from "../../types/ui";

type DropdownProps = {
  isVisible: boolean;
  setIsVisible: (isVisible: boolean) => void;
  trigger: ReactNode;
  alignment?: Alignment;
  children: ReactNode;
};

export function Dropdown({
  isVisible,
  setIsVisible,
  trigger,
  alignment = "left",
  children,
}: DropdownProps) {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsVisible(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [setIsVisible]);

  const className = [
    "dropdown",
    alignmentClasses[alignment],
    isVisible && "is-active",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div ref={dropdownRef} className={className}>
      <div className="dropdown-trigger">{trigger}</div>

      <div className="dropdown-menu" role="menu">
        <div className="dropdown-content">{children}</div>
      </div>
    </div>
  );
}
