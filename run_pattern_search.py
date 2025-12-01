# run_pattern_search.py
"""
Script para executar Pattern Search em processo separado
"""
import sys
import os
import json

# Adiciona o diretório ATUAL ao path (não o pai)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from optimizer import PatternSearch
from objective import run_external_program
import objective.external_program as ext_prog

def main():
    if len(sys.argv) < 2:
        print("Erro: Configuracao nao fornecida")
        sys.exit(1)
    
    # Carrega configuracao
    config_file = sys.argv[1]
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Configura programa externo
    ext_prog.program_path = config['program_path']
    ext_prog.program_signature = config['signature']
    ext_prog.num_params = config['num_params']
    
    x0 = config['x0']
    
    print("="*70)
    print("  PATTERN SEARCH")
    print("="*70)
    print(f"Parametros: {config['num_params']}")
    print(f"Ponto inicial: {x0}")
    print("="*70)
    print()
    
    # Executa Pattern Search
    ps = PatternSearch(
        objective_function=run_external_program,
        x0=x0,
        delta=1.0,
        delta_min=1e-6,
        max_iter=config.get('max_iter', 50)
    )
    
    ps_x, ps_f, ps_hist = ps.optimize()
    
    # Salva resultado
    result = {
        'algorithm': 'Pattern Search',
        'x': ps_x.tolist(),
        'f': float(ps_f),
        'iterations': len(ps_hist)
    }
    
    result_file = config['result_file']
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print()
    print("="*70)
    print("  PATTERN SEARCH - CONCLUIDO")
    print("="*70)
    print(f"Fitness final: {ps_f:.6f}")
    print(f"Solucao: {ps_x}")
    print(f"Iteracoes: {len(ps_hist)}")
    print("="*70)
    
    input("\nPressione Enter para fechar esta janela...")

if __name__ == "__main__":
    main()