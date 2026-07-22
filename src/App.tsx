import { useEffect } from 'react'
import { RouterProvider, createBrowserRouter, Navigate } from 'react-router-dom'
import { useStore } from './store'
import Menu from './pages/Menu'
import Roster from './pages/Roster'
import Race from './pages/Race'
import Breeding from './pages/Breeding'
import Shop from './pages/Shop'
import Settings from './pages/Settings'

const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/menu" replace /> },
  { path: '/menu', element: <Menu /> },
  { path: '/roster', element: <Roster /> },
  { path: '/race', element: <Race /> },
  { path: '/breeding', element: <Breeding /> },
  { path: '/shop', element: <Shop /> },
  { path: '/settings', element: <Settings /> },
])

export default function App() {
  const init = useStore(s => s.init)
  useEffect(() => { init() }, [init])
  return <RouterProvider router={router} />
}
