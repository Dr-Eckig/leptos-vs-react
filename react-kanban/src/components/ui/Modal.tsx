import type { ReactNode } from "react";
import { useClickOutside } from "../../hooks";
import { Button } from "./Button";

type ModalProps = {
  title: string;
  isOpen: boolean;
  close: () => void;
  saveDataTestId?: string;
  onSave: () => void;
  onDelete?: () => void;
  children: ReactNode;
};

export function Modal({
  title,
  isOpen,
  close,
  saveDataTestId,
  onSave,
  onDelete,
  children,
}: ModalProps) {
  const modalRef = useClickOutside<HTMLDivElement>(close);

  const footerClassName = [
    "modal-card-foot",
    "is-flex",
    onDelete ? "is-justify-content-space-between" : "is-justify-content-flex-end",
  ].join(" ");

  return (
    <div
      className={`modal ${isOpen ? "is-active" : ""}`}
      role="dialog"
    >
      <div className="modal-background" />

      <div className="modal-card" ref={modalRef}>
        <header className="modal-card-head">
          <p className="modal-card-title">{title}</p>

          <button
            className="delete"
            aria-label="close"
            onClick={close}
          />
        </header>

        <section className="modal-card-body">
          {children}
        </section>

        <footer className={footerClassName}>
          {onDelete && (
            <Button
              text="Delete"
              icon="trash"
              color="danger"
              onClick={onDelete}
              ariaLabel="Delete"
            />
          )}

          <div>
            <div className="buttons">
              <Button
                text="Save"
                color="success"
                onClick={onSave}
                dataTestId={saveDataTestId}
                ariaLabel="Save"
              />

              <Button
                text="Cancel"
                color="light"
                onClick={close}
                ariaLabel="Cancel"
              />
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
