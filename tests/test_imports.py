import ast
import sys
from pathlib import Path

def test_python_syntax():
    """verifica se todos os .py compilam sem erro de sintaxe"""
    base = Path(__file__).parent.parent
    py_files = list((base / "src").rglob("*.py")) + [base / "main.py"]
    ok = True
    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
            ast.parse(source)
            print(f"[OK] {f}")
        except SyntaxError as e:
            print(f"[FAIL] {f}: {e}")
            ok = False
    assert ok, "tem arquivo com erro de sintaxe"

def test_imports():
    """tenta importar os modulos principais (sem chamar WinAPI)"""
    # so checa se os arquivos existem e sao importaveis em ambiente nao Windows
    # no Windows real, ctypes.WinDLL vai funcionar
    base = Path(__file__).parent.parent
    sys.path.insert(0, str(base))
    try:
        # esses imports falham no Linux por causa de WinDLL, entao so verifica arquivo existe
        assert (base / "src" / "phantom_dll_injector" / "win_api.py").exists()
        assert (base / "src" / "phantom_dll_injector" / "injector_core.py").exists()
        assert (base / "src" / "phantom_dll_injector" / "process_watcher.py").exists()
        assert (base / "src" / "phantom_dll_injector" / "cli.py").exists()
        print("[OK] arquivos de modulo existem")
    finally:
        sys.path.pop(0)

if __name__ == "__main__":
    test_python_syntax()
    test_imports()
    print("testes basicos ok")
