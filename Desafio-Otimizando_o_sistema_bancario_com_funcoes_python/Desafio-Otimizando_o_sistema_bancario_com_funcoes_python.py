
CORERRO = '\033[91m'    # Vermelho para erros
CORPADRAO = '\033[0m'   # Cor padrão (reset)
CORSUCESSO = '\033[92m'  # Verde para sucesso

def sacar(*, saldo, valor, extrato, limite, numero_saques, LIMITE_SAQUES):
    global CORERRO, CORPADRAO, CORSUCESSO
    if valor > saldo:
        print(f"{CORERRO}Operação falhou! Você não tem saldo suficiente.{CORPADRAO}")
    elif valor > limite:
        print(f"{CORERRO}Operação falhou! O valor do saque excede o limite.{CORPADRAO}")
    elif numero_saques >= LIMITE_SAQUES:
        print(f"{CORERRO}Operação falhou! Número máximo de saques excedido.{CORPADRAO}")
    elif valor <= 0:
        print(f"{CORERRO}Operação falhou! O valor informado é inválido.{CORPADRAO}")
    else:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
    return saldo, extrato

def listar_contas(contas,usuarios):
    global CORERRO, CORSUCESSO, CORPADRAO
    if not contas:
        print(f"{CORERRO}Nenhuma conta cadastrada.{CORPADRAO}")
        return
    print("\nLista de Contas:")
    for conta in contas:
        usuario = next((u for u in usuarios if u['cpf'] == conta['usuario']), None)
        print(f"Agência: {conta['agencia']}, Número da Conta: {conta['numero_conta']}, Usuário: {usuario['nome']}")

    
    
def depositar(saldo, valor, extrato, /):
    global CORERRO, CORPADRAO, CORSUCESSO
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
    else:
        print(f"{CORERRO}Operação falhou! O valor informado é inválido.{CORPADRAO}")
    return saldo,valor, extrato
    

def contacorrente(saldo,/,*, extrato):
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================")

def criar_usuario(usuarios):
    global CORERRO, CORSUCESSO, CORPADRAO
    cpf = input("CPF (apenas números): ") 
    for usuario in usuarios: 
        if usuario['cpf'] == cpf:
            print(f"{CORERRO}CPF já cadastrado. Não é possível criar um novo usuário.{CORPADRAO}")
            return None
    nome = input("Nome do Usuário: ")
    data_nascimento = input("Data de Nascimento (dd/mm/aaaa): ")
      
    endereco = input("Endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    usuarios.append({
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco
    })
    print(f"{CORSUCESSO}Cliente {nome} criado com sucesso{CORPADRAO}")
    return usuarios

# Função para criar uma conta bancária em uma lista composta por:
# agência, número da conta, usuário
# o número de conta é sequncial iniciando em 1
# a agência é uma string com o formato: "0001"
# o usuario pode ter mais de uma conta mas uma conta pertence a um único usuário

def criar_conta(contas, usuarios):
    agencia = "0001"
    numero_conta = len(contas) + 1  
    global CORERRO, CORSUCESSO, CORPADRAO
    
    cpf_usuario = input("CPF do usuário: ")
    cpf_encontrado = any(usuario['cpf'] == cpf_usuario for usuario in usuarios)
    if not cpf_encontrado:
        print(f"{CORERRO}O usuário não se encontra cadastrado. Não é possível criar uma nova conta.{CORPADRAO}")
        return None
        
    usuario_encontrado = next((u for u in usuarios if u['cpf'] == cpf_usuario), None)
    if usuario_encontrado:
        print(f"{usuario_encontrado['nome']}.")
    contas.append({
        "agencia": agencia,
        "numero_conta": numero_conta,
        "usuario": cpf_usuario
    })
    print(f"{CORSUCESSO}Conta criada com sucesso! Agência: {agencia}, Número da Conta: {numero_conta}{CORPADRAO}")

    return contas


def menu():
    print ("""
    [c] Cadastrar cliente
    [l] Listar clientes
    [a] Criar conta
    [i] Listar contas
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [q] Sair

    => """)
    return input("Selecione uma opção: ")

def listar_usuarios(usuarios):
    global CORERRO, CORSUCESSO, CORPADRAO
    if not usuarios:
        print(f"{CORERRO}Nenhum usuário cadastrado.{CORPADRAO}")
        return
    print("\nLista de Usuários:")
    for usuario in usuarios:
        print(f"Nome: {usuario['nome']}, Data de Nascimento: {usuario['data_nascimento']}, CPF: {usuario['cpf']}, Endereço: {usuario['endereco']}")

def main():
    
    

    usuarios = []
    contas=[]

    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    LIMITE_SAQUES = 3

    while True:

        opcao=menu()

        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            saldo,valor,extrato=depositar(saldo,valor,extrato)
        elif opcao == "l":
            listar_usuarios(usuarios)
        elif opcao == "c":
            resposta = criar_usuario(usuarios)
            if resposta is not None:
                usuarios = resposta
        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))
            saldo,extrato = sacar(saque=valor, saldo=saldo, extrato=extrato, limite=limite, numero_saques=numero_saques, LIMITE_SAQUES=LIMITE_SAQUES)


        elif opcao == "e":
            contacorrente(saldo, extrato=extrato)
            

        elif opcao == "q":
            break
        elif opcao == "a":
            resposta = criar_conta(contas, usuarios)
            if resposta is not None:
                contas = resposta
        elif opcao == "i":
            listar_contas(contas, usuarios)

        else:
            print(f"{CORERRO}Operação inválida, por favor selecione novamente a operação desejada.{CORPADRAO}")

main()
