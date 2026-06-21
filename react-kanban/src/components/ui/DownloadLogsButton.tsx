import {
  performanceLogFileContent,
  performanceLogFileName,
} from "../../performance";
import { Button } from "./Button";

export function DownloadLogsButton() {
  const handleClick = () => {
    const content = performanceLogFileContent();
    const filename = performanceLogFileName();

    downloadFile(content, filename);
  };

  return (
    <Button
      text="Download Logs"
      color="light"
      icon="download"
      ariaLabel="Download performance logs as JSON file"
      dataTestId="download-logs-button"
      onClick={handleClick}
    />
  );
}

function downloadFile(content: string, filename: string) {
  const blob = new Blob([content]);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");

  a.href = url;
  a.download = filename;
  a.click();

  URL.revokeObjectURL(url);
}
