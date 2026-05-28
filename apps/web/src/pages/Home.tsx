import { Button } from "@/components/ui/button";

function alerta() {
    window.alert("Seu dispositivo foi hackeado, me envie um PIX de R$ 10.000,00");
}

function Home() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center">
      <Button onClick={() => alerta()}>Click me</Button>
    </div>
  );
}

export default Home;
