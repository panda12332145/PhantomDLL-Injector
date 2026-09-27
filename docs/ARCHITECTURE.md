# arquitetura

## visao geral

O projeto e uma ferramenta de injecao de DLL no Windows. Tem duas partes principais:

1. **injector** em Python - monitora processos e injeta DLL via WinAPI
2. **payload** em C - exemplo de DLL que executa acao ao ser carregada

```
Usuario -> CLI (main.py / src/phantom_dll_injector/cli.py)
             -> process_watcher (monitora novos PIDs)
                -> injector_core (OpenProcess, VirtualAllocEx, WriteProcessMemory, CreateRemoteThread)
                   -> DLL alvo carregada no processo remoto
                      -> DllMain da DLL cria thread e roda payload
```

## modulos

### src/phantom_dll_injector/win_api.py

Centraliza as definicoes das APIs do kernel32 e constantes. Evita repetir argtypes em todo lugar.

### src/phantom_dll_injector/injector_core.py

Funcao `inject_and_execute(pid, dll_path)`:

- abre processo com PROCESS_ALL_ACCESS
- aloca memoria remota
- escreve caminho da DLL
- pega endereco de LoadLibraryA
- cria thread remota pra carregar a DLL
- espera 3s e fecha handles

### src/phantom_dll_injector/process_watcher.py

Funcao `watch_and_inject_smart(process_name, dll_path, interval)`:

- lista processos existentes e guarda pra nao injetar neles
- loop infinito verificando psutil.process_iter
- quando acha PID novo, espera 0.5s e chama inject_and_execute
- remove PIDs que morreram
- trata KeyboardInterrupt

### src/phantom_dll_injector/cli.py

Argparse com 3 args: process, dll, --interval. Chama watcher.

### src/payload/ghost_calc_loader.c

DLL de exemplo. DllMain cria thread que roda WinExec calc.exe.

### bin/

DLLs compiladas 32 e 64 bits.

## fluxo

```
ENTRADA: nome do processo + caminho da DLL + intervalo
PROCESSAMENTO: psutil lista processos, ctypes chama WinAPI
DEPENDENCIAS: psutil, ctypes, kernel32.dll do Windows
SAIDA: logs no console e DLL injetada no processo alvo
```

## limitacoes

- so funciona no Windows por causa do kernel32 e WinAPI
- precisa privilegio suficiente pra abrir processo alvo
- arquitetura da DLL tem que bater com arquitetura do processo (x86 vs x64)
