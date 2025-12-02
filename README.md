# Sistema de Otimização Multi-Algoritmo Paralelo

Sistema de otimização que executa três algoritmos simultaneamente em processos paralelos: Pattern Search, Particle Swarm Optimization (PSO) e Híbrido (PSO + Pattern Search).

## Características Principais

- Execução paralela de três algoritmos de otimização
- Cronometragem detalhada com data e hora em cada iteração
- Divisão inteligente de threads do processador
- Compatível com qualquer programa executável externo
- Detecção automática de assinatura de parâmetros
- Interface visual em janelas CMD separadas
- Logs detalhados de progresso

## Requisitos

- Python 3.7 ou superior
- Windows (para execução paralela em janelas CMD)
- Bibliotecas Python:
  - numpy
  - tkinter (geralmente incluído no Python)

## Instalação

1. Clone ou copie todos os arquivos para um diretório
2. Instale as dependências:
```bash
   pip install numpy
```

## Estrutura do Projeto
```
PO/
├── main_parallel_fixed.py        # Script principal
├── run_pattern_search.py         # Worker Pattern Search
├── run_particle_swarm.py         # Worker Particle Swarm
├── run_hybrid.py                 # Worker Híbrido
│
├── optimizer/                    # Implementações dos algoritmos
│   ├── __init__.py
│   ├── base_optimizer.py
│   ├── pattern_search.py
│   ├── particle_swarm.py
│   └── hybrid_optimizer.py
│
├── objective/                    # Interface com programa externo
│   ├── __init__.py
│   └── external_program.py
│
└── utils/                        # Utilitários
    ├── __init__.py
    └── logger.py
```

## Uso

### Execução Básica
```bash
python main_parallel_fixed.py
```

### Fluxo de Execução

1. O sistema detecta automaticamente o número de threads do processador
2. Divide as threads entre os algoritmos que paralelizam (PSO e Híbrido)
3. Solicita a seleção do programa executável externo
4. Detecta automaticamente a assinatura de parâmetros do programa
5. Abre três janelas CMD, uma para cada algoritmo
6. Executa os três algoritmos simultaneamente
7. Aguarda a conclusão de todos os algoritmos
8. Exibe comparação dos resultados

## Algoritmos Implementados

### Pattern Search (Hooke-Jeeves)

- Algoritmo de busca direta sequencial
- Não utiliza paralelização
- Ideal para refinamento local
- Parâmetros configuráveis:
  - `max_iter`: Número máximo de iterações (padrão: 50)
  - `delta`: Tamanho inicial do passo (padrão: 1.0)
  - `delta_min`: Tamanho mínimo do passo para convergência (padrão: 1e-6)

### Particle Swarm Optimization (PSO)

- Algoritmo de inteligência de enxame
- Utiliza paralelização com threads
- Ideal para exploração global
- Parâmetros configuráveis:
  - `n_particles`: Número de partículas (padrão: 20)
  - `max_iter`: Número máximo de iterações (padrão: 30)
  - `w`: Peso de inércia (padrão: 0.7)
  - `c1`, `c2`: Coeficientes cognitivo e social (padrão: 1.5)

### Híbrido (PSO + Pattern Search)

- Combinação de exploração global e refinamento local
- Fase 1: PSO para exploração (paralelizado)
- Fase 2: Pattern Search para refinamento (sequencial)
- Parâmetros configuráveis:
  - `pso_max_iter`: Iterações da fase PSO (padrão: 20)
  - `ps_max_iter`: Iterações da fase Pattern Search (padrão: 20)
  - Demais parâmetros herdados dos algoritmos individuais

## Divisão de Threads

O sistema divide as threads automaticamente:
```
Threads Totais = N
- Pattern Search:  0 threads (algoritmo sequencial)
- Particle Swarm:  N/2 threads
- Híbrido:         N/2 threads
```

### Exemplos

**Processador com 16 threads (ex: Ryzen 7 5700X):**
- Pattern Search: 0 threads
- Particle Swarm: 8 threads
- Híbrido: 8 threads
- Aproveitamento: 100%

**Processador com 8 threads (ex: Intel i7):**
- Pattern Search: 0 threads
- Particle Swarm: 4 threads
- Híbrido: 4 threads
- Aproveitamento: 100%

**Processador com 4 threads (ex: Intel i5):**
- Pattern Search: 0 threads
- Particle Swarm: 2 threads
- Híbrido: 2 threads
- Aproveitamento: 100%

## Formato de Saída

### Logs em Tempo Real

Cada janela exibe logs com o formato:
```
[2024-12-02 21:30:45] [PSO] Iter 10: g_best = 95.234567 (tempo: 15.23s)
```

### Resultados Finais

Ao término, o sistema exibe:
- Melhor fitness encontrado por cada algoritmo
- Solução (valores dos parâmetros)
- Número de iterações realizadas
- Tempo total de execução
- Comparação entre os três algoritmos
- Melhor resultado geral

## Cronometragem

O sistema fornece três níveis de cronometragem:

1. **Tempo por iteração**: Tempo decorrido desde o início do algoritmo
2. **Tempo total por algoritmo**: Exibido ao final de cada execução
3. **Tempo de execução paralela**: Tempo total desde o início até o último algoritmo terminar

## Arquivos Temporários

Durante a execução, são criados arquivos temporários:

- `config_ps.json`: Configuração para Pattern Search
- `config_pso.json`: Configuração para Particle Swarm
- `config_hybrid.json`: Configuração para Híbrido
- `result_ps.json`: Resultado do Pattern Search
- `result_pso.json`: Resultado do Particle Swarm
- `result_hybrid.json`: Resultado do Híbrido

O sistema oferece a opção de removê-los automaticamente ao final.

## Programa Externo

O programa externo deve:

1. Aceitar parâmetros via linha de comando
2. Retornar um valor numérico via stdout
3. Ter uma assinatura consistente de parâmetros

### Tipos de Parâmetros Suportados

- Inteiros (int)
- Ponto flutuante (float)
- Double (double)

### Exemplo de Programa Compatível
```c
// programa.c
#include <stdio.h>

int main(int argc, char *argv[]) {
    int x1 = atoi(argv[1]);
    int x2 = atoi(argv[2]);
    double resultado = -(x1*x1 + x2*x2);  // Minimização
    printf("%lf\n", resultado);
    return 0;
}
```

## Detecção de Assinatura

O sistema detecta automaticamente:

- Número de parâmetros necessários
- Tipo de cada parâmetro (int, float, double)
- Limites (bounds) para parâmetros inteiros

## Portabilidade

O sistema é totalmente portável:

- Não utiliza caminhos absolutos hard-coded
- Detecta automaticamente a localização dos arquivos
- Funciona em qualquer diretório
- Compatível com diferentes configurações de hardware

## Limitações

- Apenas Windows (devido ao uso de `start cmd /k`)
- Requer que o programa externo seja executável no ambiente atual
- Pattern Search não é paralelizado (limitação algorítmica)
- Híbrido só paraleliza a fase PSO

## Exemplo de Uso Completo
```bash
# 1. Navegue até o diretório do projeto
cd C:\MeusProjetos\PO

# 2. Execute o sistema
python main_parallel_fixed.py

# 3. Selecione o programa executável quando solicitado

# 4. Aguarde a execução (janelas serão abertas automaticamente)

# 5. Verifique os resultados na janela principal
```

## Configuração Avançada

Para modificar parâmetros dos algoritmos, edite a seção de configuração em `main_parallel_fixed.py`:
```python
# Linha ~115
config_ps = create_config_file('ps', ..., max_iter=50)  # Modifique aqui
config_pso = create_config_file('pso', ..., n_particles=20, max_iter=30)
config_hybrid = create_config_file('hybrid', ..., pso_max_iter=20, ps_max_iter=20)
```

## Troubleshooting

### Erro: "Scripts não encontrados"
Certifique-se de que todos os arquivos `.py` estão no diretório raiz do projeto.

### Erro: "ModuleNotFoundError: No module named 'optimizer'"
Verifique se as pastas `optimizer/`, `objective/` e `utils/` existem e contêm os arquivos `__init__.py`.

### Janelas fecham imediatamente
Verifique se há erros de importação nos arquivos das pastas `optimizer/`, `objective/` ou `utils/`.

### Threads não são utilizadas
Certifique-se de que o NumPy está instalado corretamente e suporta operações vetorizadas.

## Licença

Este projeto foi desenvolvido para fins acadêmicos.

## Autor

Kelvin Sousa
Elson Gois
Desenvolvido como parte de projeto de Pesquisa Operacional.

## Versão

1.0.0 - Sistema completo com paralelização otimizada e cronometragem detalhada
