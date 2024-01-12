import React, { useState } from "react";
import { Provider } from "react-redux";
import { store } from "./store/store";

import { SidebarMenu } from "./components/SidebarMenu";
import { BrowserRouter as Router, Route, Link, Routes } from "react-router-dom";
import { SearchPage } from "./pages/SearchPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ToastProvider } from "./contexts/ToastContext";

export function App() {
  return (
    <Provider store={store}>
      <ToastProvider>
        <Router>
          <div className="App relative bg-gradient-to-br from-gray-100 to-blue-100 flex">
            <SidebarMenu />
            <main className="flex-1 p-6">
              <Routes>
                <Route path="/" element={<SettingsPage />} />
                <Route path="/search" element={<SearchPage />} />
              </Routes>
            </main>
          </div>
        </Router>
      </ToastProvider>
    </Provider>
  );
}
