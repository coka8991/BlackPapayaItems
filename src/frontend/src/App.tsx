import { NavLink, Routes, Route } from "react-router-dom";
import ItemsPage from "./pages/ItemsPage";
import TiersPage from "./pages/TiersPage";
import "./App.css";

function App() {
  return (
    <>
      <nav className="navbar">
        <NavLink to="/" end>
          Items
        </NavLink>
        <NavLink to="/tiers">Tiers</NavLink>
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
