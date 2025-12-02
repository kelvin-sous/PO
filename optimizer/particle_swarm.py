# optimizer/particle_swarm.py
import numpy as np
from optimizer.base_optimizer import BaseOptimizer
from datetime import datetime
import time
import os

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [PSO] {msg}")

class ParticleSwarm(BaseOptimizer):
    """Particle Swarm Optimization"""
    
    def __init__(self, objective_function, x0, 
                 n_particles=30, w=0.7, c1=1.5, c2=1.5,
                 bounds=None, n_threads=None, **kwargs):
        super().__init__(objective_function, x0, **kwargs)
        
        self.n_particles = n_particles
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.bounds = bounds or [(-10, 10)] * len(x0)
        self.history = []
        
        # Configura threads
        if n_threads is not None:
            self.n_threads = n_threads
            # Define threads para numpy (se disponível)
            try:
                os.environ['OMP_NUM_THREADS'] = str(n_threads)
                os.environ['MKL_NUM_THREADS'] = str(n_threads)
                os.environ['OPENBLAS_NUM_THREADS'] = str(n_threads)
                log(f"Threads configuradas: {n_threads}")
            except:
                pass
    
    def optimize(self):
        start_time = time.time()
        log(f"=== INICIANDO PSO ===")
        
        n_dims = len(self.x0)
        log(f"Particulas: {self.n_particles}, Dimensoes: {n_dims}")
        
        # Inicializa posicoes
        positions = np.zeros((self.n_particles, n_dims))
        for i in range(n_dims):
            low, high = self.bounds[i]
            positions[:, i] = np.random.uniform(low, high, self.n_particles)
        
        # Inicializa velocidades
        velocities = np.zeros((self.n_particles, n_dims))
        for i in range(n_dims):
            low, high = self.bounds[i]
            range_size = high - low
            velocities[:, i] = np.random.uniform(-range_size * 0.1, range_size * 0.1, self.n_particles)
        
        # Avalia particulas
        fitness = np.array([self.objective_function(p) for p in positions])
        
        p_best = positions.copy()
        p_best_fitness = fitness.copy()
        
        g_best_idx = np.argmax(fitness)
        g_best = positions[g_best_idx].copy()
        g_best_fitness = fitness[g_best_idx]
        
        elapsed = time.time() - start_time
        log(f"Fitness inicial: {g_best_fitness:.6f} (tempo: {elapsed:.2f}s)")
        
        self.history.append({
            'iteration': 0,
            'g_best': g_best.copy(),
            'g_best_fitness': g_best_fitness,
            'elapsed_time': elapsed
        })
        
        n_eval = self.n_particles
        
        for iteration in range(1, self.max_iter + 1):
            iter_start = time.time()
            
            for i in range(self.n_particles):
                r1 = np.random.random(n_dims)
                r2 = np.random.random(n_dims)
                
                cognitive = self.c1 * r1 * (p_best[i] - positions[i])
                social = self.c2 * r2 * (g_best - positions[i])
                velocities[i] = self.w * velocities[i] + cognitive + social
                
                # Limita velocidade
                for j in range(n_dims):
                    low, high = self.bounds[j]
                    v_max = (high - low) * 0.2
                    velocities[i, j] = np.clip(velocities[i, j], -v_max, v_max)
                
                positions[i] = positions[i] + velocities[i]
                
                # Limites de posicao
                for j in range(n_dims):
                    low, high = self.bounds[j]
                    positions[i, j] = np.clip(positions[i, j], low, high)
                
                fitness[i] = self.objective_function(positions[i])
                n_eval += 1
                
                if fitness[i] > p_best_fitness[i]:
                    p_best[i] = positions[i].copy()
                    p_best_fitness[i] = fitness[i]
                    
                    if fitness[i] > g_best_fitness:
                        g_best = positions[i].copy()
                        g_best_fitness = fitness[i]
                        elapsed = time.time() - start_time
                        log(f"Iter {iteration}: Nova melhor -> f = {g_best_fitness:.6f} (tempo: {elapsed:.2f}s)")
            
            elapsed = time.time() - start_time
            if iteration % 10 == 0:
                log(f"Iter {iteration}: g_best = {g_best_fitness:.6f} (tempo: {elapsed:.2f}s)")
            
            self.history.append({
                'iteration': iteration,
                'g_best': g_best.copy(),
                'g_best_fitness': g_best_fitness,
                'elapsed_time': elapsed
            })
            
            if np.std(fitness) < self.tol:
                log(f"Convergencia: std < tol")
                break
        
        total_time = time.time() - start_time
        log(f"=== CONCLUIDO ===")
        log(f"Melhor fitness: {g_best_fitness:.6f}")
        log(f"Avaliacoes: {n_eval}")
        log(f"TEMPO TOTAL: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")
        
        return g_best, g_best_fitness, self.history