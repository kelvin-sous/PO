import subprocess
import tkinter as tk
from tkinter import filedialog
import re

program_path = None
program_signature = []
num_params = 0


def select_program():
    """Abre o explorador de arquivos para selecionar o executavel."""
    global program_path

    root = tk.Tk()
    root.withdraw()
    program_path = filedialog.askopenfilename(
        title="Selecione o executavel do programa",
        filetypes=[("Executaveis", "*.exe"), ("Scripts Python", "*.py"), ("Todos os arquivos", "*.*")]
    )

    if not program_path:
        raise FileNotFoundError("Nenhum executavel selecionado.")
    
    print(f"Executavel selecionado: {program_path}")
    return program_path


def test_program_with_params(params):
    """Testa o programa com parametros."""
    global program_path
    
    if program_path is None:
        raise ValueError("Programa nao selecionado.")
    
    try:
        str_params = [str(p) for p in params]
        cmd = [program_path] + str_params
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            return False, output, error
        
        try:
            float(output)
            return True, output, error
        except ValueError:
            return False, output, error
            
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def parse_help_output_advanced(output):
    """Parser avancado para mensagem de ajuda."""
    
    # Padrao 1: "x1 x2 x3 x4 x5"
    x_pattern = re.findall(r'\bx\d+\b', output)
    if x_pattern:
        num = len(x_pattern)
        print(f"Detectado {num} parametros pelo padrao 'x1 x2 x3...'")
        
        if 'inteiro' in output.lower() or 'integer' in output.lower():
            types = ['int'] * num
            print("Tipo: inteiro")
        elif 'float' in output.lower() or 'real' in output.lower():
            types = ['float'] * num
            print("Tipo: float")
        else:
            types = ['int'] * num
            print("Tipo: int (padrao)")
        
        # Detecta limites
        bounds_match = re.search(r'(\d+)\s*a\s*(\d+)', output)
        if bounds_match:
            min_val = int(bounds_match.group(1))
            max_val = int(bounds_match.group(2))
            print(f"Limites detectados: {min_val} a {max_val}")
            bounds = [(min_val, max_val)] * num
        else:
            bounds = None
        
        return {'found': True, 'num_params': num, 'types': types, 'bounds': bounds}
    
    # Padrao 2: "[int] [float]"
    bracket_pattern = re.findall(r'\[(int|float|double|string|str|text)\]', output)
    if bracket_pattern:
        types = []
        for t in bracket_pattern:
            if t == 'int':
                types.append('int')
            elif t in ['float', 'double']:
                types.append('float')
            else:
                types.append('str')
        
        print(f"Detectado {len(types)} parametros pelo padrao [tipo]")
        return {'found': True, 'num_params': len(types), 'types': types, 'bounds': None}
    
    return {'found': False, 'num_params': 0, 'types': [], 'bounds': None}


def try_get_help_info():
    """Tenta extrair informacoes usando --help."""
    global program_path
    
    help_attempts = [["--help"], ["-h"], ["--usage"], ["-help"], []]
    
    for args in help_attempts:
        try:
            cmd = [program_path] + args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            output = (result.stdout + result.stderr)
            
            if output:
                print(f"Tentativa com {args or '[sem args]'}: {len(output)} caracteres")
                parsed = parse_help_output_advanced(output)
                if parsed['found']:
                    return parsed
        except:
            continue
    
    return {'found': False, 'num_params': 0, 'types': [], 'bounds': None}


def detect_num_params_by_testing():
    """Detecta numero de parametros testando."""
    global program_path
    
    print("Detectando numero de parametros por teste...")
    
    for n in range(1, 11):
        test_params = [50] * n
        success, output, error = test_program_with_params(test_params)
        
        if success:
            print(f"Programa aceita {n} parametros")
            return n, True
        else:
            print(f"Teste com {n} parametros falhou")
    
    print("Nao foi possivel detectar numero de parametros")
    return None, False


def detect_param_types(num_params):
    """Detecta tipos dos parametros."""
    global program_path
    
    print(f"Detectando tipos dos {num_params} parametros...")
    
    types = []
    
    for i in range(num_params):
        base_params = [50] * num_params
        
        # Teste com inteiro
        test_params_int = base_params.copy()
        test_params_int[i] = 10
        success_int, output_int, _ = test_program_with_params(test_params_int)
        
        # Teste com float
        test_params_float = base_params.copy()
        test_params_float[i] = 10.5
        success_float, output_float, _ = test_program_with_params(test_params_float)
        
        if success_int and not success_float:
            param_type = "int"
            print(f"  Parametro {i+1}: INT")
        elif success_float:
            param_type = "float"
            print(f"  Parametro {i+1}: FLOAT")
        else:
            param_type = "int"
            print(f"  Parametro {i+1}: INT (padrao)")
        
        types.append(param_type)
    
    return types


def detect_program_signature_smart():
    """Deteccao automatica da assinatura do programa."""
    global program_path, program_signature, num_params
    
    if program_path is None:
        select_program()
    
    print("="*60)
    print("DETECCAO AUTOMATICA DE ASSINATURA")
    print("="*60)
    
    # Etapa 1: Tentar --help
    print("\nEtapa 1: Tentando --help...")
    help_info = try_get_help_info()
    
    if help_info['found']:
        print("Informacoes encontradas via --help")
        num_params = help_info['num_params']
        program_signature = help_info['types']
        bounds = help_info.get('bounds')
    else:
        # Etapa 2: Teste
        print("\nEtapa 2: Deteccao por teste...")
        detected_num, success = detect_num_params_by_testing()
        
        if not success or detected_num is None:
            print("Usando configuracao padrao: 2 floats")
            num_params = 2
            program_signature = ["float", "float"]
            bounds = None
        else:
            num_params = detected_num
            print(f"\nEtapa 3: Detectando tipos dos {num_params} parametros...")
            program_signature = detect_param_types(num_params)
            bounds = None
    
    print("\n" + "="*60)
    print("ASSINATURA DETECTADA:")
    print(f"  Numero de parametros: {num_params}")
    print(f"  Tipos: {program_signature}")
    print("="*60 + "\n")
    
    return program_signature, num_params, bounds


def run_external_program(params):
    """Executa o programa com parametros."""
    global program_path, program_signature, num_params

    if program_path is None:
        select_program()

    if not program_signature or num_params == 0:
        detect_program_signature_smart()

    if len(params) != num_params:
        raise ValueError(f"Numero incorreto de parametros! Esperado: {num_params}, Recebido: {len(params)}")

    # Converte parametros
    converted = []
    for p, t in zip(params, program_signature):
        if t == "int":
            converted.append(str(int(round(p))))
        elif t == "float":
            converted.append(f"{float(p):.10f}")
        else:
            converted.append(str(p))

    cmd = [program_path] + converted
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"Programa retornou erro: {error_msg}")
        
        output = result.stdout.strip()
        
        try:
            value = float(output)
            return value
        except ValueError:
            raise ValueError(f"Saida inesperada: '{output}'")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("Timeout")
    except Exception as e:
        raise RuntimeError(f"Erro ao executar: {e}")


def get_program_info():
    """Retorna informacoes sobre o programa."""
    global program_path, program_signature, num_params
    
    return {
        'path': program_path,
        'num_params': num_params,
        'signature': program_signature,
        'detected': bool(program_signature)
    }