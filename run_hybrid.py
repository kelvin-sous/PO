# run_hybrid.py
"""
Script para executar Hybrid Optimizer em processo separado
"""
import sys
import os
import json

# Adiciona o diretório ATUAL ao path (não o pai)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from optimizer import HybridPSOPatternSearch
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
    bounds = config.get('bounds')
    
    print("="*70)
    print("  HYBRID PSO + PATTERN SEARCH")
    print("="*70)
    print(f"Parametros: {config['num_params']}")
    print(f"Ponto inicial: {x0}")
    print(f"Particulas: {config.get('n_particles', 20)}")
    print("="*70)
    print()
    
    hyb = HybridPSOPatternSearch(
        objective_function=run_external_program,
        x0=x0,
        n_particles=config.get('n_particles', 20),
        pso_max_iter=config.get('pso_max_iter', 20),
        ps_max_iter=config.get('ps_max_iter', 20),
        bounds=bounds,
        n_threads=config.get('n_threads')
    )
    
    hyb_x, hyb_f, hyb_hist = hyb.optimize()
    
    # Salva resultado
    result = {
        'algorithm': 'Hybrid',
        'x': hyb_x.tolist(),
        'f': float(hyb_f),
        'iterations': hyb_hist['phases'][-1]['iterations']
    }
    
    result_file = config['result_file']
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print()
    print("="*70)
    print("  HYBRID - CONCLUIDO")
    print("="*70)
    print(f"Fitness final: {hyb_f:.6f}")
    print(f"Solucao: {hyb_x}")
    print(f"Fases completadas: {len(hyb_hist['phases'])}")
    print("="*70)
    
    input("\nPressione Enter para fechar esta janela...")

if __name__ == "__main__":
    main()