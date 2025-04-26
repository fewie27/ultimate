import React from "react";
import ReactDOM from "react-dom/client";
import Upload from "./Upload";
import Analysis from "./Analysis";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <Analysis/>
  </React.StrictMode>
);
