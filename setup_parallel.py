# setup_parallel.py
"""
Script de Setup - Copia os arquivos necessarios para execucao paralela
Execute este script UMA VEZ para configurar o sistema
"""

import os
import shutil

def setup_parallel_execution():
    print("="*70)
    print("  SETUP - SISTEMA DE EXECUCAO PARALELA")
    print("="*70)
    print()
    
    # Diretório atual (onde este script está)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lista de arquivos necessários
    required_files = [
        'main_parallel_fixed.py',
        'run_pattern_search.py',
        'run_particle_swarm.py',
        'run_hybrid.py'
    ]
    
    print("Verificando arquivos necessarios...\n")
    
    missing_files = []
    for filename in required_files:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} - NAO ENCONTRADO")
            missing_files.append(filename)
    
    if missing_files:
        print("\n" + "="*70)
        print("ERRO: Arquivos faltando!")
        print("="*70)
        print("\nOs seguintes arquivos estao faltando:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPor favor, coloque todos os arquivos na mesma pasta.")
        input("\nPressione Enter para sair...")
        return False
    
    print("\n" + "="*70)
    print("Todos os arquivos encontrados!")
    print("="*70)
    
    # Verifica estrutura de pastas
    print("\nVerificando estrutura de pastas...\n")
    
    required_dirs = ['optimizer', 'objective', 'utils']
    missing_dirs = []
    
    for dirname in required_dirs:
        dirpath = os.path.join(current_dir, dirname)
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            print(f"  ✓ {dirname}/")
        else:
            print(f"  ✗ {dirname}/ - NAO ENCONTRADO")
            missing_dirs.append(dirname)
    
    if missing_dirs:
        print("\n" + "="*70)
        print("AVISO: Pastas faltando!")
        print("="*70)
        print("\nAs seguintes pastas estao faltando:")
        for d in missing_dirs:
            print(f"  - {d}/")
        print("\nCertifique-se de que a estrutura completa do projeto esta presente.")
        input("\nPressione Enter para continuar mesmo assim...")
    else:
        print("\n" + "="*70)
        print("Estrutura de pastas OK!")
        print("="*70)
    
    print("\n" + "="*70)
    print("SETUP CONCLUIDO COM SUCESSO!")
    print("="*70)
    print("\nVoce pode agora executar:")
    print("\n  python main_parallel_fixed.py")
    print("\nPara iniciar a otimizacao paralela.")
    print("="*70)
    
    input("\nPressione Enter para sair...")
    return True

if __name__ == "__main__":
    setup_parallel_execution()