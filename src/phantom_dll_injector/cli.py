import argparse
from .process_watcher import watch_and_inject_smart


def main():
    parser = argparse.ArgumentParser(description='Monitor inteligente de injecao de DLL')
    parser.add_argument('process', help='Nome do processo alvo')
    parser.add_argument('dll', help='Caminho completo da DLL')
    parser.add_argument('--interval', type=int, default=3, help='Intervalo de verificacao')

    args = parser.parse_args()
    watch_and_inject_smart(args.process, args.dll, args.interval)


if __name__ == '__main__':
    main()
