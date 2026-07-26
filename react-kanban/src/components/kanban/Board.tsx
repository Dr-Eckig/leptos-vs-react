import { useBoardsState, useModalsState } from "../../hooks";
import { DownloadLogsButton } from "../ui/DownloadLogsButton";
import { Sidebar } from "./Sidebar";
import { TaskColumn } from "./Column";
import { BoardModal, ColumnModal, TaskModal } from "./modals";

export function Board() {
  const { currentBoard } = useBoardsState();
  const modals = useModalsState();
  const boardColumns = currentBoard?.columns ?? [];

  return (
    <div className="is-flex">
      <Sidebar />
      <div className="container is-fluid page-height">
        <section className="section is-flex is-flex-direction-column full-height px-0">
          <div className="is-flex is-justify-content-end pr-3">
            <DownloadLogsButton />
          </div>
          <div className="columns is-flex-grow-1 full-height m-0">
            {boardColumns.map((column) => (
              <TaskColumn key={column.id} column={column} />
            ))}
          </div>
          {modals.board && <BoardModal data={modals.board} />}
          {modals.column && <ColumnModal data={modals.column} />}
          {modals.task && <TaskModal data={modals.task} />}
        </section>
      </div>
    </div>
  );
}
