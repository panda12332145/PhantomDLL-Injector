# como compilar o payload

O arquivo `ghost_calc_loader.c` e um exemplo de DLL que abre a calculadora quando carregada.

## Windows com MinGW

```bash
# 32 bits
gcc -shared -o ../../bin/ghost_calc_payload_x86.dll ghost_calc_loader.c -Wl,--subsystem,windows

# 64 bits
gcc -shared -o ../../bin/ghost_calc_payload_x64.dll ghost_calc_loader.c -Wl,--subsystem,windows
```

## Visual Studio (cl)

```bash
cl /LD ghost_calc_loader.c /Fe:../../bin/ghost_calc_payload_x64.dll
```

A DLL usa `DllMain` e cria uma thread separada pra executar o payload, evita travar o loader lock.
