# consideracoes de seguranca

## o que o projeto faz

- abre processos com PROCESS_ALL_ACCESS (0x1F0FFF)
- aloca memoria remota e escreve caminho de DLL
- cria thread remota que chama LoadLibraryA
- isso e injecao de codigo, tecnica sensivel

## riscos reais encontrados

- **PROCESS_ALL_ACCESS**: permissao maxima, se o codigo for usado contra processo privilegiado pode escalar. Impacto: acesso total ao processo alvo. Recomendacao: usar direitos minimos necessarios quando possivel, tipo PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_QUERY_INFORMATION.

- **sem validacao de caminho da DLL**: o usuario passa qualquer caminho, nao tem checagem se arquivo existe ou e confiavel antes de injetar. Impacto: injecao de DLL maliciosa se caminho for manipulado. Recomendacao: validar existencia do arquivo e talvez checar assinatura.

- **sem sanitizacao de nome de processo**: nome vem direto da CLI e compara lower(). Nao e vulneravel a injecao classica, mas se for usado em automacao sem validacao pode injetar em processo errado. Impacto: baixo, mas vale checar.

- **psutil e ctypes com tratamento generico de excecao**: varios `except:` sem tipo especifico escondem erros. Impacto: dificulta debug e pode mascarar falha de seguranca. Recomendacao: logar excecao especifica.

- **DLL exemplo executa calc.exe via WinExec**: WinExec e API legada e pode ser flagged por AV. Nao e vulnerabilidade, mas e comportamento que chama atencao. Recomendacao: usar CreateProcess se for expandir.

- **sem controle de privilegio**: nao verifica se esta rodando como admin. Se tentar injetar em processo protegido vai falhar silenciosamente. Impacto: baixo.

- **binarios versionados**: as DLLs compiladas estao no repo. Binarios no git dificultam auditoria. Recomendacao: compilar em CI ou deixar instrucao de build, nao versionar binario, ou usar release no GitHub.

## o que NAO existe

- nao tem autenticacao
- nao tem criptografia
- nao tem comunicacao de rede
- nao tem banco de dados
- nao tem secrets hardcoded (verificado nos arquivos .py e .c)

## recomendacoes gerais

- use apenas em ambiente de teste controlado
- nunca injete DLL desconhecida em processo de terceiros
- valide arquitetura x86/x64 antes de injetar
- rode com menor privilegio possivel
- considere adicionar log de auditoria
