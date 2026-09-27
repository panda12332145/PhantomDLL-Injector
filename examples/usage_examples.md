# exemplos de uso

## uso basico via main.py

```bash
python main.py notepad.exe C:\caminho\para\bin\ghost_calc_payload_x64.dll --interval 3
```

Isso monitora novas instancias de `notepad.exe` e injeta a DLL quando detectar.

## uso como modulo

```python
from src.phantom_dll_injector import watch_and_inject_smart

watch_and_inject_smart("notepad.exe", "C:\\caminho\\para\\bin\\ghost_calc_payload_x64.dll", 3)
```

## injecao direta em PID

```python
from src.phantom_dll_injector import inject_and_execute

pid = 1234
ok = inject_and_execute(pid, "C:\\caminho\\para\\bin\\ghost_calc_payload_x64.dll")
print("injetado" if ok else "falhou")
```

## compilacao do payload

Veja `src/payload/build_instructions.md`.
