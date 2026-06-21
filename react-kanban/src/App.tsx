import mockData from "../mock_data/mock_board.json";
import { Board } from "./components/kanban";
import { AppContextProvider } from "./hooks";
import { deserializeAllBoards, type RawAllBoards } from "./types/serialize";

function App() {
  const initialBoards = deserializeAllBoards(mockData as RawAllBoards);

  return (
    <AppContextProvider initialBoards={initialBoards}>
      <Board />
    </AppContextProvider>
  );
}

export default App;
