import time
import psutil

from .injector_core import inject_and_execute


def watch_and_inject_smart(process_name: str, dll_path: str, check_interval: int = 5):
    """monitora o sistema e injeta so em instancias novas do processo alvo"""

    print(f"[*] Monitorando processo: {process_name}")
    print(f"[*] DLL: {dll_path}")
    print(f"[*] Intervalo: {check_interval}s")
    print("[*] Modo: injecao apenas em novas instancias\n")

    # guarda pids que ja existem pra nao injetar neles
    known_processes = {}

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                known_processes[proc.info['pid']] = proc.create_time()
                print(f"[i] Processo existente encontrado: PID {proc.info['pid']} (nao injetado)")
        except Exception:
            continue

    print("[*] Aguardando novas instancias...\n")

    try:
        while True:
            current_pids = set()

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == process_name.lower():
                        pid = proc.info['pid']
                        current_pids.add(pid)

                        if pid not in known_processes:
                            creation_time = proc.create_time()
                            known_processes[pid] = creation_time

                            print(f"[+] [{time.strftime('%H:%M:%S')}] Nova instancia detectada: PID {pid}")

                            # espera um pouco pro processo terminar de subir
                            time.sleep(0.5)

                            if inject_and_execute(pid, dll_path):
                                print("    DLL injetada com sucesso!")
                            else:
                                print("    Falha na injecao")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # limpa pids que ja morreram
            dead_pids = set(known_processes.keys()) - current_pids
            for dead_pid in dead_pids:
                print(f"[-] [{time.strftime('%H:%M:%S')}] Processo PID {dead_pid} terminou")
                del known_processes[dead_pid]

            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n[!] Monitoramento interrompido")
