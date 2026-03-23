import { useState } from "react";
import { NavLink, Routes, Route } from "react-router-dom";
import ItemsPage from "./pages/ItemsPage";
import TiersPage from "./pages/TiersPage";
import { refreshData } from "./api";
import "./App.css";

function App() {
  const [reloading, setReloading] = useState(false);

  const handleReload = async () => {
    setReloading(true);
    try {
      await refreshData();
      window.location.reload();
    } finally {
      setReloading(false);
    }
  };

  return (
    <>
      <nav className="navbar">
        <NavLink to="/" end>
          Items
        </NavLink>
        <NavLink to="/tiers">Tiers</NavLink>
        <button className="reload-btn" onClick={handleReload} disabled={reloading}>
          {reloading ? "Reloading…" : "⟳ Reload"}
        </button>
      </nav>
      <main className="content">
        <Routes>
          <Route path="/" element={<ItemsPage />} />
          <Route path="/tiers" element={<TiersPage />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
