# main.py
"""
Script principal SIMPLIFICADO - executa os 3 algoritmos sequencialmente
"""

from optimizer import PatternSearch, ParticleSwarm, HybridPSOPatternSearch
from objective import select_program, detect_program_signature_smart, run_external_program
from utils import log
import objective.external_program as ext_prog
import json

def main():
    print("="*70)
    print("  SISTEMA DE OTIMIZACAO MULTI-ALGORITMO")
    print("="*70)
    print()
    
    # Seleciona programa
    log("Selecione o executavel...")
    program_path = select_program()
    
    # Detecta assinatura
    log("Detectando assinatura...")
    signature, num_params, bounds = detect_program_signature_smart()
    
    # Configura
    ext_prog.program_path = program_path
    ext_prog.program_signature = signature
    ext_prog.num_params = num_params
    
    x0 = [50.5] * num_params if bounds else [0.0] * num_params
    
    log(f"Configuracao: {num_params} parametros, tipos: {signature}")
    log(f"Ponto inicial: {x0}")
    
    # Executa os 3 algoritmos
    results = {}
    
    # 1. Pattern Search
    print("\n" + "="*70)
    log("EXECUTANDO: PATTERN SEARCH")
    print("="*70)
    ps = PatternSearch(
        objective_function=run_external_program,
        x0=x0,
        delta=1.0,
        delta_min=1e-6,
        max_iter=50  # Reduzido para teste
    )
    ps_x, ps_f, ps_hist = ps.optimize()
    results['Pattern Search'] = {'x': ps_x, 'f': ps_f, 'iter': len(ps_hist)}
    
    # 2. Particle Swarm
    print("\n" + "="*70)
    log("EXECUTANDO: PARTICLE SWARM")
    print("="*70)
    pso = ParticleSwarm(
        objective_function=run_external_program,
        x0=x0,
        n_particles=20,  # Reduzido
        bounds=bounds,
        max_iter=30  # Reduzido
    )
    pso_x, pso_f, pso_hist = pso.optimize()
    results['Particle Swarm'] = {'x': pso_x, 'f': pso_f, 'iter': len(pso_hist)}
    
    # 3. Hybrid
    print("\n" + "="*70)
    log("EXECUTANDO: HYBRID")
    print("="*70)
    hyb = HybridPSOPatternSearch(
        objective_function=run_external_program,
        x0=x0,
        n_particles=20,
        pso_max_iter=20,
        ps_max_iter=20,
        bounds=bounds
    )
    hyb_x, hyb_f, hyb_hist = hyb.optimize()
    results['Hybrid'] = {'x': hyb_x, 'f': hyb_f, 'iter': hyb_hist['phases'][-1]['iterations']}
    
    # Mostra comparação
    print("\n" + "="*70)
    log("COMPARACAO FINAL")
    print("="*70)
    for name, res in results.items():
        log(f"{name}:")
        log(f"  Fitness: {res['f']:.6f}")
        log(f"  Solucao: {res['x']}")
        log(f"  Iteracoes: {res['iter']}")
    
    # Melhor
    best = max(results.items(), key=lambda x: x[1]['f'])
    print("\n" + "="*70)
    log(f"MELHOR: {best[0]} com fitness {best[1]['f']:.6f}")
    print("="*70)
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()