# Banco Python - Simulação de um sistema bancário simples
# Este código simula um sistema bancário simples com opções de levantar, depositar e extrato.
# Importa a biblioteca msvcrt para capturar entradas do teclado sem pressionar Enter
import msvcrt

limite_saque = 500 # Limite de saque por transação
saldo = 0 # Saldo inicial da conta
limite_movimentacao = 5000 # Limite de depósitos 
saques_diarios = 3 # Limite de saques diários 3
saques_realizados = 0 # Contador de saques realizados hoje
extrato = [] # Lista para armazenar o extrato de movimentações

err="\033[91m" # Código de erro (vermelho)
ok="\033[92m" # Código de sucesso (verde)
normal="\033[0m" # Código normal (reset)

mensagem= ""

# Limpa a tela do console
def limpar_tela():
    print("\033[H\033[J", end='')

# Funções para as operações bancárias
def depositar():
    global saldo, limite_movimentacao, extrato, mensagem
    print("\n=== Depósito ===")
    try:
        valor = float(input("Digite o valor a ser depositado: "))
        if valor <= 0:
            mensagem = f"{err}\nValor inválido. O depósito deve ser maior que zero.{normal}"
            return
        if valor + saldo > limite_movimentacao:
            mensagem = f"{err}\nLimite de movimentação excedido. O depósito não foi realizado.{normal}"
            return
        saldo += valor
        extrato.append(f"Depósito: R$ {valor:.2f}")
        mensagem = f"{ok}\nDepósito realizado com sucesso! Saldo atual: R$ {saldo:.2f}{normal}"
    except ValueError:
        mensagem = f"{err}\nEntrada inválida. Por favor, digite um número válido.{normal}"

def estrato():
    global extrato, mensagem
    limpar_tela()
    print("\n=== Extrato ===")
    if not extrato:
        print("\nNenhuma movimentação registrada.")
    else:
        print("\nMovimentações:")
        for mov in extrato:
            print(mov)
        print(f"\nSaldo atual: R$ {saldo:.2f}")
    input("\nPressione qualquer tecla para continuar...")

def levantar():
    global saldo, limite_saque, extrato, mensagem, saques_realizados
    global saques_diarios
    print("\n=== Levantar ===")
    try:
        valor = float(input("Digite o valor a ser levantado: "))
        if valor <= 0:
            mensagem = f"{err}\nValor inválido. O levantamento deve ser maior que zero.{normal}"
            return
        if valor > saldo:
            mensagem = f"{err}\nSaldo insuficiente para o levantamento.{normal}"
            return
        if valor > limite_saque:
            mensagem = f"{err}\nValor excede o limite de saque de R$ {limite_saque:.2f}.{normal}"
            return
        if saques_realizados >= saques_diarios:
            mensagem = f"{err}\nLimite de saques diários excedido. Você já realizou {saques_realizados} saques hoje.{normal}"
            return
        saldo -= valor
        saques_realizados+=1
        extrato.append(f"Levantamento: R$ {valor:.2f}")
        mensagem = f"{ok}\nLevantamento realizado com sucesso! Saldo atual: R$ {saldo:.2f}{normal}"
    except ValueError:
        mensagem = f"{err}\nEntrada inválida. Por favor, digite um número válido.{normal}"

# Função para exibir o menu principal
def menu_principal():
    print("=== Banco Python ===")
    print("1. Levantar")
    print("2. Despositar")
    print("3. Extrato")
    print("0. Sair")
    print("Escolha uma opção: ", end='', flush=True)
    opcao = msvcrt.getwch()
    return opcao

# Loop principal do programa
while True:
    limpar_tela()
    print (mensagem)
    mensagem = ""  
    opcao = menu_principal()
    if opcao == '1':
        levantar()
    elif opcao == '2':
        depositar()
    elif opcao == '3':
        estrato()
    elif opcao == '0':
        print("\nSaindo do programa...")
        break
    else:
        mensagem=f"{err}\nOpção inválida. Tente novamente.{normal}"
    
    
