import ctypes
from ctypes import wintypes
import psutil
import time
import sys

# Constantes
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Configurações das APIs
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE

VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
VirtualAllocEx.restype = wintypes.LPVOID

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
WriteProcessMemory.restype = wintypes.BOOL

GetModuleHandleA = kernel32.GetModuleHandleA
GetModuleHandleA.argtypes = [wintypes.LPCSTR]
GetModuleHandleA.restype = wintypes.HMODULE

GetProcAddress = kernel32.GetProcAddress
GetProcAddress.argtypes = [wintypes.HMODULE, wintypes.LPCSTR]
GetProcAddress.restype = wintypes.LPVOID

CreateRemoteThread = kernel32.CreateRemoteThread
CreateRemoteThread.argtypes = [wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID]
CreateRemoteThread.restype = wintypes.HANDLE

WaitForSingleObject = kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
WaitForSingleObject.restype = wintypes.DWORD

CloseHandle = kernel32.CloseHandle

def inject_and_execute(pid: int, dll_path: str):
    """Injeta DLL e força execução via CreateRemoteThread em export function"""
    try:
        h_process = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not h_process:
            return False

        dll_path_bytes = dll_path.encode('utf-8')
        size = len(dll_path_bytes) + 1
        
        # Aloca memória para o caminho da DLL
        remote_mem = VirtualAllocEx(h_process, None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not remote_mem:
            CloseHandle(h_process)
            return False

        # Escreve o caminho da DLL
        written = ctypes.c_size_t(0)
        WriteProcessMemory(h_process, remote_mem, dll_path_bytes, size, ctypes.byref(written))
        
        # Carrega a DLL
        h_kernel32 = GetModuleHandleA(b'kernel32.dll')
        load_lib_addr = GetProcAddress(h_kernel32, b'LoadLibraryA')
        
        h_thread = CreateRemoteThread(h_process, None, 0, load_lib_addr, remote_mem, 0, None)
        if h_thread:
            # Espera a DLL carregar
            WaitForSingleObject(h_thread, 3000)
            CloseHandle(h_thread)
            
            # Se a DLL tem uma função exportada, podemos chamá-la
            # Isso força a execução mesmo se a DLL já estava carregada
            # (implementação avançada - precisaria de GetProcAddress remoto)
            
            CloseHandle(h_process)
            return True
        
        CloseHandle(h_process)
        return False
    except:
        return False

def watch_and_inject_smart(process_name: str, dll_path: str, check_interval: int = 5):
    """Monitora e injeta APENAS em NOVAS instâncias do processo"""
    print(f"[*] Monitorando processo: {process_name}")
    print(f"[*] DLL: {dll_path}")
    print(f"[*] Intervalo: {check_interval}s")
    print("[*] Modo: Injeção apenas em novas instâncias\n")
    
    # Dicionário para rastrear processos: {pid: creation_time}
    known_processes = {}
    
    # Inicializa com processos existentes (NÃO injeta neles)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                known_processes[proc.info['pid']] = proc.create_time()
                print(f"[i] Processo existente encontrado: PID {proc.info['pid']} (não injetado)")
        except:
            continue
    
    print(f"[*] Aguardando novas instâncias...\n")
    
    try:
        while True:
            current_pids = set()
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == process_name.lower():
                        pid = proc.info['pid']
                        current_pids.add(pid)
                        
                        # Se é um PID novo que não conhecíamos
                        if pid not in known_processes:
                            creation_time = proc.create_time()
                            known_processes[pid] = creation_time
                            
                            print(f"[+] [{time.strftime('%H:%M:%S')}] Nova instância detectada: PID {pid}")
                            
                            # Pequena pausa para o processo inicializar completamente
                            time.sleep(0.5)
                            
                            if inject_and_execute(pid, dll_path):
                                print(f"    ✓ DLL injetada com sucesso!")
                            else:
                                print(f"    ✗ Falha na injeção")
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Remove processos que já terminaram
            dead_pids = set(known_processes.keys()) - current_pids
            for dead_pid in dead_pids:
                print(f"[-] [{time.strftime('%H:%M:%S')}] Processo PID {dead_pid} terminou")
                del known_processes[dead_pid]
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n[!] Monitoramento interrompido")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Monitor inteligente de injeção de DLL')
    parser.add_argument('process', help='Nome do processo alvo')
    parser.add_argument('dll', help='Caminho completo da DLL')
    parser.add_argument('--interval', type=int, default=3, help='Intervalo de verificação')
    
    args = parser.parse_args()
    watch_and_inject_smart(args.process, args.dll, args.interval)