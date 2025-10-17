import { Routes, Route, Navigate } from "react-router-dom";
import { Suspense } from "react";
import { routes } from "./routes";

export default function App() {
  return (
    <Suspense fallback={null}>
      <Routes>
        {routes.map((r, i) => <Route key={i} path={r.path} element={r.element} />)}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
