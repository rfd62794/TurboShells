/**
 * React Router Configuration
 * 
 * Maps PyGame scene_controller states to web routes.
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';

// Lazy load routes for code splitting
const MainMenu = lazy(() => import('./MainMenu'));
const RosterView = lazy(() => import('./RosterView'));
const RaceView = lazy(() => import('./RaceView'));
const BreedingLab = lazy(() => import('./BreedingLab'));
const Shop = lazy(() => import('./Shop'));
const Settings = lazy(() => import('./Settings'));

// Loading fallback
const LoadingScreen = () => (
    <div className="loading-screen">
        <div className="loading-spinner">🐢</div>
        <p>Loading...</p>
    </div>
);

// Wrap lazy components
const withSuspense = (Component: React.LazyExoticComponent<() => JSX.Element>) => (
    <Suspense fallback={<LoadingScreen />}>
        <Component />
    </Suspense>
);

export const router = createBrowserRouter([
    {
        path: '/',
        element: <Navigate to="/menu" replace />,
    },
    {
        path: '/menu',
        element: withSuspense(MainMenu),
    },
    {
        path: '/roster',
        element: withSuspense(RosterView),
    },
    {
        path: '/race',
        element: withSuspense(RaceView),
    },
    {
        path: '/breeding',
        element: withSuspense(BreedingLab),
    },
    {
        path: '/shop',
        element: withSuspense(Shop),
    },
    {
        path: '/settings',
        element: withSuspense(Settings),
    },
]);
