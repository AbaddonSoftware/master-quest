import { lazy } from "react";
import type { RouteObject } from "react-router-dom";
import RequireAuth from "../guards/RequireAuth";
import RequireDisplayName from "../guards/RequireDisplayName";

const Landing = lazy(() => import("../pages/Landing"));
const SetDisplayNamePage = lazy(() => import("../pages/Onboarding"));
const CreateRoomPage = lazy(() => import("../pages/CreateRoomPage"));

export const routes: RouteObject[] = [
  { path: "/", 
    element: 
    <Landing /> },
  { path: "/onboarding", 
    element: (
    <RequireAuth>
      <SetDisplayNamePage />
    </RequireAuth> 
    )
  },
  { path: "/rooms/new",
    element: (
      <RequireAuth>
        <RequireDisplayName>
          <CreateRoomPage />
        </RequireDisplayName>
      </RequireAuth>
    )
  },
];
