import type { ReactNode } from "react";
import { Button } from "./Button";

type ModalProps = {
  title: string;
  isOpen: boolean;
  onClose: () => void;
  saveDataTestId?: string;
  onSave: () => void;
  onDelete?: () => void;
  children: ReactNode;
};

export function Modal({
  title,
  isOpen,
  onClose,
  saveDataTestId,
  onSave,
  onDelete,
  children,
}: ModalProps) {
  const footerClassName = [
    "modal-card-foot",
    "is-flex",
    onDelete ? "is-justify-content-space-between" : "is-justify-content-flex-end",
  ].join(" ");

  return (
    <div
      className={`modal ${isOpen ? "is-active" : ""}`}
      role="dialog"
      aria-modal={isOpen}
      aria-hidden={!isOpen}
    >
      <div className="modal-background" onMouseDown={onClose} />

      <div className="modal-card">
        <header className="modal-card-head">
          <p className="modal-card-title">{title}</p>

          <button
            className="delete"
            aria-label="close"
            onClick={onClose}
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
              onClick={onClose}
              ariaLabel="Cancel"
            />
          </div>
        </footer>
      </div>
    </div>
  );
}
