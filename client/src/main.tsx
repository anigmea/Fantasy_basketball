import { Provider } from "./components/ui/provider"
import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import Home from "./pages/Home";
import BoomBust from "./pages/BoomBust";
import Schedule from "./pages/Schedule";
import Replacements from "./pages/Replacements";
import Trades from "./pages/Trades";


const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,        // Wrap App to include <Outlet />
    children: [
      { path: "/players", element: <Home /> },
      { path: "boombust", element: <BoomBust /> },
      { path: "schedule", element: <Schedule /> },
      { path: "replacements", element: <Replacements /> },
      { path: "trades", element: <Trades /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Provider>
      <RouterProvider router={router} />
    </Provider>
  </React.StrictMode>
);