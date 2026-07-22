import { RouterProvider } from 'react-router-dom';
import { useEffect } from 'react';
import { router } from './routes/router';
import { useGameStore } from './stores';
import './styles/retro.css';

function AppInit() {
    const init = useGameStore(s => s.init);
    useEffect(() => { init(); }, [init]);
    return null;
}

export default function App() {
    return (
        <>
            <AppInit />
            <RouterProvider router={router} />
        </>
    );
}
