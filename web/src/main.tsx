import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import "./index.css";
import { useAppStore } from "./store/useAppStore";

function Root() {
  const theme = useAppStore((s) => s.theme);
  return (
    <>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      <Toaster theme={theme} richColors position="top-right" />
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
);
