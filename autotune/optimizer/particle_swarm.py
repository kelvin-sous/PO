import numpy as np
from .base_optimizer import BaseOptimizer

def log(msg):
    print(f"[PSO] {msg}")

class ParticleSwarm(BaseOptimizer):
    """Particle Swarm Optimization"""
    
    def __init__(self, objective_function, x0, 
                 n_particles=30, w=0.7, c1=1.5, c2=1.5,
                 bounds=None, **kwargs):
        super().__init__(objective_function, x0, **kwargs)
        
        self.n_particles = n_particles
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.bounds = bounds or [(-10, 10)] * len(x0)
        self.history = []
    
    def optimize(self):
        n_dims = len(self.x0)
        
        log(f"Iniciando - {self.n_particles} particulas, {n_dims} dimensoes")
        
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
        
        log(f"Fitness inicial: {g_best_fitness:.6f}")
        
        self.history.append({
            'iteration': 0,
            'g_best': g_best.copy(),
            'g_best_fitness': g_best_fitness
        })
        
        n_eval = self.n_particles
        
        for iteration in range(1, self.max_iter + 1):
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
                        improvement = fitness[i] - g_best_fitness
                        g_best = positions[i].copy()
                        g_best_fitness = fitness[i]
                        log(f"Iter {iteration}: Nova melhor solucao - f = {g_best_fitness:.6f}")
            
            if iteration % 10 == 0:
                log(f"Iter {iteration}: g_best = {g_best_fitness:.6f}")
            
            self.history.append({
                'iteration': iteration,
                'g_best': g_best.copy(),
                'g_best_fitness': g_best_fitness
            })
            
            if np.std(fitness) < self.tol:
                log(f"Convergencia: std < tol")
                break
        
        log(f"Concluido: f* = {g_best_fitness:.6f}, {n_eval} avaliacoes")
        return g_best, g_best_fitness, self.history