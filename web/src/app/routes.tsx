import { lazy } from "react";
import type { RouteObject } from "react-router-dom";
import RequireAuth from "../guards/RequireAuth";
import RequireDisplayName from "../guards/RequireDisplayName";

const Landing = lazy(() => import("../pages/Landing"));
const SetDisplayNamePage = lazy(() => import("../pages/Onboarding"));
const CreateRoomPage = lazy(() => import("../pages/CreateRoomPage"));
const RoomBoardPage = lazy(() => import("../pages/RoomBoardPage"));
const RoomsOverviewPage = lazy(() => import("../pages/RoomsOverviewPage"));

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
  {
    path: "/rooms/:roomId",
    element: (
      <RequireAuth>
        <RequireDisplayName>
          <RoomBoardPage />
        </RequireDisplayName>
      </RequireAuth>
    ),
  },
  {
    path: "/rooms",
    element: (
      <RequireAuth>
        <RequireDisplayName>
          <RoomsOverviewPage />
        </RequireDisplayName>
      </RequireAuth>
    ),
  },
];
