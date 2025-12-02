# main_parallel_fixed.py
"""
Script principal - executa os 3 algoritmos em PARALELO (VERSÃO OTIMIZADA)
Com cronômetro, data/hora e divisão inteligente de threads
"""

import subprocess
import sys
import os
import json
import time
import multiprocessing

# Garante que o diretório atual está no path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from objective import select_program, detect_program_signature_smart
from utils import log

def get_optimal_threads():
    """Detecta número de threads e divide APENAS entre os algoritmos que paralelizam"""
    total_threads = multiprocessing.cpu_count()
    
    # Pattern Search NÃO paraleliza
    # Divide threads APENAS entre PSO e Hybrid (50% cada)
    threads_pso = total_threads // 2
    threads_hybrid = total_threads // 2
    
    # Se for ímpar, dá a thread extra para o PSO (geralmente mais pesado)
    if total_threads % 2 != 0:
        threads_pso += 1
    
    print("\n" + "="*70)
    print("CONFIGURACAO DE THREADS")
    print("="*70)
    print(f"Threads disponiveis no sistema: {total_threads}")
    print(f"")
    print(f"Divisao por algoritmo:")
    print(f"  - Pattern Search:  0 threads (algoritmo sequencial)")
    print(f"  - Particle Swarm:  {threads_pso} threads")
    print(f"  - Hybrid (PSO+PS): {threads_hybrid} threads")
    print(f"")
    print(f"Total alocado: {threads_pso + threads_hybrid} de {total_threads} threads")
    print(f"Aproveitamento: {((threads_pso + threads_hybrid) / total_threads * 100):.1f}%")
    print("="*70)
    
    return {
        'pattern_search': 0,
        'particle_swarm': threads_pso,
        'hybrid': threads_hybrid
    }

def create_config_file(name, program_path, signature, num_params, x0, bounds, n_threads, **kwargs):
    """Cria arquivo de configuracao para um algoritmo"""
    config = {
        'program_path': program_path,
        'signature': signature,
        'num_params': num_params,
        'x0': x0,
        'bounds': bounds,
        'result_file': f'result_{name}.json',
        'n_threads': n_threads,
        **kwargs
    }
    
    config_file = f'config_{name}.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return os.path.abspath(config_file)

def wait_for_results(result_files, timeout=300):
    """Aguarda todos os arquivos de resultado serem criados"""
    print("\nAguardando conclusao dos algoritmos...")
    print("(Isso pode levar alguns minutos...)")
    start_time = time.time()
    
    completed = set()
    
    while time.time() - start_time < timeout:
        for rf in result_files:
            if rf not in completed and os.path.exists(rf):
                completed.add(rf)
                algo_name = rf.replace('result_', '').replace('.json', '').upper()
                elapsed = time.time() - start_time
                print(f"  ✓ {algo_name} concluido! (tempo decorrido: {elapsed:.2f}s)")
        
        if len(completed) == len(result_files):
            time.sleep(1)
            return True
        
        time.sleep(2)
    
    return False

def load_results(result_files):
    """Carrega resultados dos arquivos JSON"""
    results = {}
    for result_file in result_files:
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    results[result['algorithm']] = result
            except Exception as e:
                print(f"Erro ao ler {result_file}: {e}")
        else:
            print(f"Arquivo nao encontrado: {result_file}")
    return results

def cleanup_temp_files():
    """Remove arquivos temporarios"""
    temp_files = [
        'config_ps.json', 'config_pso.json', 'config_hybrid.json',
        'result_ps.json', 'result_pso.json', 'result_hybrid.json'
    ]
    for f in temp_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass

def main():
    print("="*70)
    print("  SISTEMA DE OTIMIZACAO MULTI-ALGORITMO (PARALELO OTIMIZADO)")
    print("="*70)
    print()
    
    # Limpa arquivos antigos
    cleanup_temp_files()
    
    # Seleciona programa
    log("Selecione o executavel...")
    program_path = select_program()
    
    # Detecta assinatura
    log("Detectando assinatura...")
    signature, num_params, bounds = detect_program_signature_smart()
    
    x0 = [50.5] * num_params if bounds else [0.0] * num_params
    
    log(f"Configuracao: {num_params} parametros, tipos: {signature}")
    log(f"Ponto inicial: {x0}")
    
    # Detecta e divide threads
    thread_config = get_optimal_threads()
    
    # Cria arquivos de configuracao com threads
    print("\nPreparando configuracoes...")
    config_ps = create_config_file('ps', program_path, signature, num_params, x0, bounds,
                                   n_threads=thread_config['pattern_search'], max_iter=50)
    
    config_pso = create_config_file('pso', program_path, signature, num_params, x0, bounds,
                                    n_threads=thread_config['particle_swarm'], 
                                    n_particles=20, max_iter=30)
    
    config_hybrid = create_config_file('hybrid', program_path, signature, num_params, x0, bounds,
                                       n_threads=thread_config['hybrid'], n_particles=20, 
                                       pso_max_iter=20, ps_max_iter=20)
    
    # Determina caminhos ABSOLUTOS
    python_exe = sys.executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    script_ps = os.path.join(current_dir, 'run_pattern_search.py')
    script_pso = os.path.join(current_dir, 'run_particle_swarm.py')
    script_hybrid = os.path.join(current_dir, 'run_hybrid.py')
    
    # Verifica se os scripts existem
    missing_scripts = []
    if not os.path.exists(script_ps):
        missing_scripts.append('run_pattern_search.py')
    if not os.path.exists(script_pso):
        missing_scripts.append('run_particle_swarm.py')
    if not os.path.exists(script_hybrid):
        missing_scripts.append('run_hybrid.py')
    
    if missing_scripts:
        print("\n" + "="*70)
        print("ERRO: Scripts nao encontrados!")
        print("="*70)
        print("\nOs seguintes arquivos estao faltando no diretorio atual:")
        for script in missing_scripts:
            print(f"  - {script}")
        print(f"\nDiretorio atual: {current_dir}")
        print("\nPor favor, certifique-se de que todos os arquivos estao presentes.")
        input("\nPressione Enter para sair...")
        return
    
    print("\n" + "="*70)
    print("INICIANDO ALGORITMOS EM PARALELO...")
    print("="*70)
    print()
    
    execution_start = time.time()
    
    # Prepara comandos
    cmd_ps = ['cmd', '/c', 'start', 'Pattern Search', 'cmd', '/k', python_exe, script_ps, config_ps]
    print(f"[1/3] Iniciando Pattern Search...")
    subprocess.Popen(cmd_ps, cwd=current_dir)
    time.sleep(0.5)
    
    cmd_pso = ['cmd', '/c', 'start', 'Particle Swarm', 'cmd', '/k', python_exe, script_pso, config_pso]
    print(f"[2/3] Iniciando Particle Swarm...")
    subprocess.Popen(cmd_pso, cwd=current_dir)
    time.sleep(0.5)
    
    cmd_hybrid = ['cmd', '/c', 'start', 'Hybrid Optimizer', 'cmd', '/k', python_exe, script_hybrid, config_hybrid]
    print(f"[3/3] Iniciando Hybrid...")
    subprocess.Popen(cmd_hybrid, cwd=current_dir)
    
    print()
    print("="*70)
    print("Tres janelas de comando foram abertas!")
    print("Cada janela mostra o progresso com data/hora e cronometro.")
    print("="*70)
    print()
    
    # Aguarda resultados
    result_files = ['result_ps.json', 'result_pso.json', 'result_hybrid.json']
    
    if wait_for_results(result_files, timeout=600):
        total_execution_time = time.time() - execution_start
        
        print("\n" + "="*70)
        print("TODOS OS ALGORITMOS CONCLUIRAM!")
        print("="*70)
        print(f"Tempo total de execucao paralela: {total_execution_time:.2f}s ({total_execution_time/60:.2f} min)")
        print()
        
        # Carrega e exibe resultados
        results = load_results(result_files)
        
        if results:
            print("="*70)
            print("COMPARACAO FINAL")
            print("="*70)
            
            for name, res in sorted(results.items()):
                print(f"\n{name}:")
                print(f"  Fitness: {res['f']:.6f}")
                print(f"  Solucao: {res['x']}")
                print(f"  Iteracoes: {res['iterations']}")
                if 'execution_time' in res:
                    print(f"  Tempo: {res['execution_time']:.2f}s")
            
            # Melhor resultado
            if len(results) > 0:
                best_name = max(results.items(), key=lambda x: x[1]['f'])[0]
                best_f = results[best_name]['f']
                
                print("\n" + "="*70)
                print(f"MELHOR RESULTADO: {best_name}")
                print(f"Fitness: {best_f:.6f}")
                print("="*70)
        else:
            print("Nenhum resultado foi carregado com sucesso.")
    else:
        print("\nTimeout: Alguns algoritmos ainda estao executando.")
        print("Verifique as janelas abertas para o progresso.")
    
    # Pergunta se deve limpar arquivos temporarios
    print()
    cleanup = input("\nDeseja remover arquivos temporarios? (s/n): ")
    if cleanup.lower() == 's':
        cleanup_temp_files()
        print("Arquivos temporarios removidos.")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()