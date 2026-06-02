import seabreeze.spectrometers as sb
import seabreeze
import time
import numpy as np
import paho.mqtt.client as mqtt

seabreeze.use("pyseabreeze")

spec = None

def on_message(client, userdata, msg):
    global ligado, setTemp, micros, Start, spec, reator_ativo
    comando = msg.payload.decode()
    print(f"[Espectrômetro] Comando recebido: {comando}")

    if spec is None:
        print("⚠️ Espectrômetro não inicializado ainda")
        return

    # Comando para selecionar reator automaticamente quando ligar
    if comando == "ligar_r1":
        reator_ativo = "1"
        ligado = True
        Start = False  
        print(f"🎯 Espectrômetro agora enviando dados para Reator 1 (Ligado)")
        return

    if comando == "ligar_r2":
        reator_ativo = "2"
        ligado = True
        Start = False  
        print(f"🎯 Espectrômetro agora enviando dados para Reator 2 (Ligado)")
        return

    # Comandos normais (só executa se o reator for "1" ou "2")
    if reator_ativo not in ["1", "2"]:
        return

    if comando == "desligar":
        ligado = False
        Start = False
        reator_ativo = None
        print(f"🔴 Espectrômetro desligado")
    elif comando == "Start":
        if not ligado:
            print("⚠️ Não é possível iniciar: espectrômetro desligado")
        else:
            Start = True
    elif comando == "Pause":
        if not ligado:
            print("⚠️ Espectrômetro já está desligado")
        else:
            Start = False
    elif comando.startswith("set_integration:"):
        try:
            _, valor = comando.split(":")
            micros = int(valor)
            setTemp = True
            print(f"⏱️ Tempo de integração alterado para {micros} µs")
        except Exception as e:
            print(f"❌ Erro ao alterar tempo de integração: {e}")
    elif comando == "request_wavelengths":
        try:
            wavelengths = spec.wavelengths().astype(np.float32)
            client.publish(f"reator{reator_ativo}/espectrometro_w", wavelengths.tobytes())
            print("📤 Wavelengths reenviados a pedido do frontend")
        except Exception as e:
            print(f"❌ Erro ao reenviar wavelengths: {e}")
    elif comando.startswith("set_trigger"):
        if ligado and Start:
            print("⏸️ Pausando aquisição para trocar modo de trigger")
            Start = False
            time.sleep(0.2)  # garante que a leitura atual terminou

        try:
            if comando == "set_trigger:free":
                spec.trigger_mode(0)
                print("🔁 Modo do espectrômetro: FREE RUNNING")

            elif comando == "set_trigger:external":
                spec.trigger_mode(3)
                print("⚡ Modo do espectrômetro: TRIGGER EXTERNO")

        except Exception as e:
            print(f"❌ Erro ao trocar modo de trigger: {e}")


# Variáveis globais
ligado = False
setTemp = False
micros = 100_000
Start = False
reator_ativo = None

client = mqtt.Client()
client.on_message = on_message
client.connect("192.168.0.100", 1883, 60)
client.subscribe("espectrometro/comando")  # Tópico único para controlar o espectrômetro
client.loop_start()

def safe_intensities_read(spec, max_attempts=5):
    """Tenta ler intensidades com múltiplas tentativas"""
    for attempt in range(max_attempts):
        try:
            intensities = spec.intensities()
            return intensities
        except KeyboardInterrupt:
            raise
        except ValueError as e:
            if "broadcast" in str(e) or "shape" in str(e):
                print(f"Tentativa {attempt + 1}/{max_attempts} falhou - erro de comunicação")
                time.sleep(0.2)
            else:
                raise e
    raise Exception(f"Falha após {max_attempts} tentativas de leitura")

# --- Conecta no espectrômetro ---
while spec is None:
    devices = sb.list_devices()
    print(devices)
    if devices:
        spec = sb.Spectrometer(devices[0])

        # --- DELAY DE INICIALIZAÇÃO ---
        print("Inicializando espectrômetro...")
        time.sleep(2.0)

        # --- Configura tempo de integração ---
        spec.integration_time_micros(micros)
        time.sleep(0.5)

        # Envia wavelengths para ambos os reators inicialmente
        wavelengths = spec.wavelengths().astype(np.float32)
        client.publish("reator1/espectrometro_w", wavelengths.tobytes())
        client.publish("reator2/espectrometro_w", wavelengths.tobytes())
        print(f"📤 Wavelengths enviados para ambos os reatores: {len(wavelengths)} pontos")

        last_send_time = 0
        min_send_interval = 0.1

        try:
            while True:
                if setTemp:
                    try:
                        spec.integration_time_micros(micros)
                        time.sleep(0.5)
                        print(f"⏱️ Tempo de integração alterado para {micros} µs")
                        setTemp = False
                    except Exception as e:
                        print(f"❌ Erro ao aplicar novo tempo: {e}")

                if ligado and Start and reator_ativo in ["1", "2"]:
                    try:
                        current_time = time.time()
                        if current_time - last_send_time >= min_send_interval:
                            intensities = safe_intensities_read(spec).astype(np.float32)
                            client.publish(f"reator{reator_ativo}/espectrometro_int", intensities.tobytes())
                            last_send_time = current_time
                            print(f"📤 Intensidades enviadas para Reator {reator_ativo}: {len(intensities)} pontos")
                        else:
                            time.sleep(0.01)
                    except Exception as e:
                        print(f"Erro na leitura: {e}")
                else:
                    time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        finally:
            if spec is not None:
                try:
                    spec.close()
                    print("✅ Espectrômetro fechado")
                except Exception as e:
                    print("⚠️ Erro ao fechar espectrômetro:", e)
            client.loop_stop()
            client.disconnect()
            print("👋 Encerrado com segurança")
    else:
        print("Nenhum dispositivo encontrado!")
    time.sleep(2)