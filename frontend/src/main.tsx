import React from "react";
import ReactDOM from "react-dom/client";
import Upload from "./Upload"; // falls du die Komponente in Upload.tsx auslagerst
// oder hier einfach direkt verwenden, wenn alles in main.tsx bleibt

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <Upload />
  </React.StrictMode>
);
