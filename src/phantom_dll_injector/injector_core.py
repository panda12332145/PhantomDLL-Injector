import ctypes
from .win_api import (
    OpenProcess,
    VirtualAllocEx,
    WriteProcessMemory,
    GetModuleHandleA,
    GetProcAddress,
    CreateRemoteThread,
    WaitForSingleObject,
    CloseHandle,
    PROCESS_ALL_ACCESS,
    MEM_COMMIT,
    MEM_RESERVE,
    PAGE_READWRITE,
)


def inject_and_execute(pid: int, dll_path: str) -> bool:
    """injeta a dll no processo alvo e forca execucao via CreateRemoteThread"""

    try:
        h_process = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not h_process:
            return False

        dll_path_bytes = dll_path.encode('utf-8')
        size = len(dll_path_bytes) + 1

        # aloca espaco la no processo remoto pra escrever o caminho da dll
        remote_mem = VirtualAllocEx(h_process, None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not remote_mem:
            CloseHandle(h_process)
            return False

        written = ctypes.c_size_t(0)
        WriteProcessMemory(h_process, remote_mem, dll_path_bytes, size, ctypes.byref(written))

        # pega LoadLibraryA e cria thread remota pra carregar a dll
        h_kernel32 = GetModuleHandleA(b'kernel32.dll')
        load_lib_addr = GetProcAddress(h_kernel32, b'LoadLibraryA')

        h_thread = CreateRemoteThread(h_process, None, 0, load_lib_addr, remote_mem, 0, None)
        if h_thread:
            WaitForSingleObject(h_thread, 3000)
            CloseHandle(h_thread)
            CloseHandle(h_process)
            return True

        CloseHandle(h_process)
        return False
    except Exception:
        # se der qualquer erro no meio, considera falha
        return False
