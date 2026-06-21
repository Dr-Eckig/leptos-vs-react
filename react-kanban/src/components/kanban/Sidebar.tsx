import { IconText } from "../ui/IconText";
import {
  useBoardsActions,
  useBoardsState,
  useModalsActions,
} from "../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
} from "../../performance";
import { openBoardModal, openBoardModalWithBoard } from "../../types/modals";
import { iconClasses, type FontawesomeIcon } from "../ui/icons";

type SidebarItemProps = {
  label: string;
  isActive: boolean;
  onClick: () => void;
  dataTestId?: string;
  icon?: FontawesomeIcon;
  onEdit?: () => void;
};

export function Sidebar() {
  const { boards, currentBoard, currentBoardId } = useBoardsState();
  const boardActions = useBoardsActions();
  const modalActions = useModalsActions();

  return (
    <aside className="menu has-background-light px-3 py-5">
      <ul className="menu-list">
        <SidebarItem
          label="Add Board"
          icon="circlePlus"
          isActive={false}
          dataTestId="add-board-button"
          onClick={() => {
            const finishMeasurement = startPerformanceMeasurement(
              PerformanceAction.ModalOpen,
              performanceContextFromBoard(currentBoard),
            );
            modalActions.setBoard(openBoardModal());
            finishMeasurement();
          }}
        />
      </ul>
      <p className="menu-label">
        Boards
      </p>
      <ul className="menu-list">
        {boards.map((board, index) => (
          <SidebarItem
            key={board.id}
            label={board.title}
            isActive={currentBoardId === board.id}
            dataTestId={`sidebar-board-${index}`}
            onClick={() => {
              if (currentBoardId === board.id) {
                return;
              }

              const finishMeasurement = startPerformanceMeasurement(
                PerformanceAction.BoardSwitch,
                performanceContextFromBoard(board),
              );
              boardActions.setCurrentBoard(board.id);
              finishMeasurement();
            }}
            onEdit={() => {
              const finishMeasurement = startPerformanceMeasurement(
                PerformanceAction.ModalOpen,
                performanceContextFromBoard(currentBoard),
              );
              modalActions.setBoard(openBoardModalWithBoard(board));
              finishMeasurement();
            }}
          />
        ))}
      </ul>
    </aside>
  );
}

function SidebarItem({
  label,
  isActive,
  onClick,
  dataTestId,
  icon,
  onEdit,
}: SidebarItemProps) {
  
  const buttonClass = isActive
        ? "has-background-link is-active"
        : "has-background-light";

  return (
    <li className="sidebar-item">
      <button
        className={buttonClass}
        onClick={onClick}
        data-testid={dataTestId}
      >
        {icon ? (
          <IconText icon={icon} text={label} />
        ) : (
          <div className="is-flex is-justify-content-space-between">
            {label}

            {onEdit && (
              <div
                className="edit-button ml-2"
                onClick={(event) => {
                  event.stopPropagation();
                  onEdit();
                }}
              >
                <i className={iconClasses["ellipsis"]} />
              </div>
            )}
          </div>
        )}
      </button>
    </li>
  );
}
