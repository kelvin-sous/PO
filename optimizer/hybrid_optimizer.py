import numpy as np
from optimizer.base_optimizer import BaseOptimizer
from optimizer.particle_swarm import ParticleSwarm
from optimizer.pattern_search import PatternSearch

def log(msg):
    print(f"[HYBRID] {msg}")

class HybridPSOPatternSearch(BaseOptimizer):
    """Hibrido: PSO + Pattern Search"""
    
    def __init__(self, objective_function, x0,
                 n_particles=30, w=0.7, c1=1.5, c2=1.5, pso_max_iter=100,
                 delta=0.1, delta_min=1e-6, reduction_factor=0.5, ps_max_iter=100,
                 bounds=None, **kwargs):
        super().__init__(objective_function, x0, **kwargs)
        
        self.n_particles = n_particles
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.pso_max_iter = pso_max_iter
        
        self.delta = delta
        self.delta_min = delta_min
        self.reduction_factor = reduction_factor
        self.ps_max_iter = ps_max_iter
        
        self.bounds = bounds or [(-10, 10)] * len(x0)
        self.history = {'pso': [], 'pattern_search': [], 'phases': []}
    
    def optimize(self):
        log("Iniciando otimizacao hibrida")
        
        # FASE 1: PSO
        log("FASE 1: PSO - Exploracao global")
        pso = ParticleSwarm(
            objective_function=self.objective_function,
            x0=self.x0,
            n_particles=self.n_particles,
            w=self.w,
            c1=self.c1,
            c2=self.c2,
            bounds=self.bounds,
            max_iter=self.pso_max_iter,
            tol=self.tol
        )
        
        pso_best_x, pso_best_f, pso_history = pso.optimize()
        self.history['pso'] = pso_history
        
        log(f"PSO concluido: f = {pso_best_f:.6f}")
        
        # FASE 2: Pattern Search
        log("FASE 2: Pattern Search - Refinamento local")
        ps = PatternSearch(
            objective_function=self.objective_function,
            x0=pso_best_x,
            delta=self.delta,
            delta_min=self.delta_min,
            reduction_factor=self.reduction_factor,
            max_iter=self.ps_max_iter,
            tol=self.tol
        )
        
        ps_best_x, ps_best_f, ps_history = ps.optimize()
        self.history['pattern_search'] = ps_history
        
        log(f"Pattern Search concluido: f = {ps_best_f:.6f}")
        
        # Resultados
        self.history['phases'].append({
            'phase': 'PSO',
            'best_x': pso_best_x.copy(),
            'best_f': pso_best_f,
            'iterations': len(pso_history)
        })
        
        self.history['phases'].append({
            'phase': 'Pattern Search',
            'best_x': ps_best_x.copy(),
            'best_f': ps_best_f,
            'iterations': len(ps_history)
        })
        
        log(f"Hibrido concluido: f* = {ps_best_f:.6f}")
        return ps_best_x, ps_best_f, self.history