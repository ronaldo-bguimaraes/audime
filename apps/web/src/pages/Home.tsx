import { Button } from "@/components/ui/button";

import { Link } from "react-router";

function Home() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 py-8 sm:px-6 lg:px-8">
            <div className="space-y-3 text-center">
                <h1 className="text-4xl font-semibold tracking-tight text-foreground">Audime</h1>
                <p className="max-w-md text-sm text-muted-foreground">
                    Abra o scanner QR integrado ao tema do app e leia códigos usando a câmera do dispositivo.
                </p>
            </div>
            <Link to="/scanner">
                <Button className="w-full max-w-xs">
                    Abrir scanner QR
                </Button>
            </Link>
        </div>
    );
}

export default Home;
