# run_particle_swarm.py
"""
Script para executar Particle Swarm em processo separado
"""
import sys
import os
import json

# Adiciona o diretório ATUAL ao path (não o pai)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from optimizer import ParticleSwarm
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
    print("  PARTICLE SWARM OPTIMIZATION")
    print("="*70)
    print(f"Parametros: {config['num_params']}")
    print(f"Ponto inicial: {x0}")
    print(f"Particulas: {config.get('n_particles', 20)}")
    print("="*70)
    print()
    
    # Executa PSO
    pso = ParticleSwarm(
        objective_function=run_external_program,
        x0=x0,
        n_particles=config.get('n_particles', 20),
        bounds=bounds,
        max_iter=config.get('max_iter', 30)
    )
    
    pso_x, pso_f, pso_hist = pso.optimize()
    
    # Salva resultado
    result = {
        'algorithm': 'Particle Swarm',
        'x': pso_x.tolist(),
        'f': float(pso_f),
        'iterations': len(pso_hist)
    }
    
    result_file = config['result_file']
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print()
    print("="*70)
    print("  PARTICLE SWARM - CONCLUIDO")
    print("="*70)
    print(f"Fitness final: {pso_f:.6f}")
    print(f"Solucao: {pso_x}")
    print(f"Iteracoes: {len(pso_hist)}")
    print("="*70)
    
    input("\nPressione Enter para fechar esta janela...")

if __name__ == "__main__":
    main()