import etcd3
import time
import os
import json

# Mapeamento de nomes de nó para IPs na sua rede Docker (ajuste se sua subnet for diferente)
NODE_IP_MAPPING = {
    "mx-nodel": "172.21.0.10",
    "mx-nodel2": "172.21.0.11",
    "mx-nodel3": "172.21.0.12",
}

# Obtém o nome do nó e IP a partir do ambiente do container
process_id = os.environ.get('NODE_NAME', 'mx-nodel')
etcd_host = NODE_IP_MAPPING.get(process_id, "172.21.0.10")

# Conexão com o etcd
try:
    client = etcd3.client(host=etcd_host, port=2379)
    print(f"[{process_id}] Conectado ao etcd em {etcd_host}:2379")
except Exception as e:
    print(f"[{process_id}] Erro ao conectar ao etcd: {e}")
    exit(1)

# Variável global para o relógio lógico local do processo
logical_clock = 0

def update_lamport_clock():
    global logical_clock # Permite modificar a variável global

    try:
        # 1. Incrementa o relógio local para qualquer evento (interno ou antes de enviar)
        logical_clock += 1

        # 2. Ler o valor atual do relógio lógico global do etcd
        #    A chave armazena um JSON: {"value": C_global, "process_id": ID_ultimo_atualizador}
        global_data_bytes, _ = client.get('/lamport_clock')
        global_data = json.loads(global_data_bytes.decode('utf-8')) if global_data_bytes else {"value": 0, "process_id": None}
        
        global_clock_etcd = global_data["value"]

        # 3. Atualizar relógio local: max(relógio_local_atual, relógio_global_etcd) + 1
        logical_clock = max(logical_clock, global_clock_etcd) + 1

        # 4. Preparar o novo valor global para o etcd (incluindo ID do processo)
        new_global_data = {
            "value": logical_clock,
            "process_id": process_id,
            "real_timestamp": time.time() # Timestamp real para observação, não é parte do Lamport puro
        }

        # 5. Armazenar o novo valor global no etcd
        client.put('/lamport_clock', json.dumps(new_global_data))
        
        print(f"[{process_id}] Relógio Lógico: {logical_clock} (Último atualizador global: {global_data.get('process_id', 'Nenhum')})")
        return logical_clock
    except Exception as e:
        print(f"[{process_id}] Erro ao atualizar relógio Lamport: {e}")
        return None

if __name__ == "__main__":
    print(f"Iniciando serviço de relógio Lamport em {process_id}...")
    try:
        while True:
            update_lamport_clock()
            time.sleep(2) # Atualiza a cada 2 segundos para demonstrar a concorrência
    except KeyboardInterrupt:
        print(f"[{process_id}] Serviço de relógio Lamport interrompido.")
    except Exception as e:
        print(f"[{process_id}] Ocorreu um erro inesperado: {e}")
