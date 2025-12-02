# optimizer/pattern_search.py
import numpy as np
from optimizer.base_optimizer import BaseOptimizer
from datetime import datetime
import time

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [PS] {msg}")

class PatternSearch(BaseOptimizer):
    """Pattern Search (Hooke-Jeeves)"""

    def __init__(self, objective_function, x0, delta=1.0, 
                 delta_min=1e-6, reduction_factor=0.5, **kwargs):
        super().__init__(objective_function, x0, **kwargs)
        self.delta = delta
        self.delta_min = delta_min
        self.reduction_factor = reduction_factor
        self.history = []

    def optimize(self):
        start_time = time.time()
        log(f"=== INICIANDO PATTERN SEARCH ===")
        
        x = np.array(self.x0, dtype=float)
        n_dims = len(x)
        
        f_best = self.objective_function(x)
        self.history.append({'iteration': 0, 'x': x.copy(), 'f': f_best, 'delta': self.delta})
        
        log(f"Fitness inicial: f(x0) = {f_best:.6f}")

        delta = self.delta
        n_eval = 1

        for iteration in range(1, self.max_iter + 1):
            iter_start = time.time()
            improved = False
            
            for i in range(n_dims):
                if improved:
                    break
                
                for direction in [1, -1]:
                    x_new = np.copy(x)
                    x_new[i] += direction * delta
                    
                    f_new = self.objective_function(x_new)
                    n_eval += 1

                    if f_new > f_best:
                        elapsed = time.time() - start_time
                        log(f"Iter {iteration}: Melhoria dim {i} -> f = {f_new:.6f} (tempo: {elapsed:.2f}s)")
                        
                        x = x_new
                        f_best = f_new
                        improved = True
                        
                        self.history.append({
                            'iteration': iteration,
                            'x': x.copy(),
                            'f': f_best,
                            'delta': delta,
                            'improved': True,
                            'elapsed_time': elapsed
                        })
                        break

            if not improved:
                delta *= self.reduction_factor
                if iteration % 5 == 0:
                    elapsed = time.time() - start_time
                    log(f"Iter {iteration}: Sem melhoria, delta = {delta:.6f} (tempo: {elapsed:.2f}s)")
                
                self.history.append({
                    'iteration': iteration,
                    'x': x.copy(),
                    'f': f_best,
                    'delta': delta,
                    'improved': False,
                    'elapsed_time': time.time() - start_time
                })

            if delta < self.delta_min:
                log(f"Convergencia: delta ({delta:.2e}) < delta_min")
                break

        total_time = time.time() - start_time
        log(f"=== CONCLUIDO ===")
        log(f"Melhor fitness: {f_best:.6f}")
        log(f"Avaliacoes: {n_eval}")
        log(f"TEMPO TOTAL: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")
        
        return x, f_best, self.history