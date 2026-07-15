import type { ReactNode } from "react";
import { useClickOutside } from "../../hooks";
import {
  type Alignment,
  alignmentClasses,
} from "../../types/ui";

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
  const dropdownRef = useClickOutside<HTMLDivElement>(() => setIsVisible(false));

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

      <div className="dropdown-menu" id="dropdown-menu" role="menu">
        <div className="dropdown-content">{children}</div>
      </div>
    </div>
  );
}
