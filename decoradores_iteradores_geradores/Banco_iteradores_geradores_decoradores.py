from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
import os
from functools import wraps

_TRANSACTION_ID = 0
def get_next_transaction_id():
    global _TRANSACTION_ID
    _TRANSACTION_ID += 1
    return _TRANSACTION_ID


def log_transacao(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Executa a função original primeiro
        resultado = func(*args, **kwargs)

        # Lógica de log baseada no tipo de função/retorno
        if isinstance(args[0], Transacao): # Para Deposito e Saque (onde args[0] é a transacao)
            transacao = args[0]
            conta = args[1] #  registrar(self, conta)
            tipo = type(transacao).__name__
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Transação: {tipo} | ID: {transacao.id} | Valor: R${transacao.valor:.2f} | Conta: {conta.numero}")
        elif func.__name__ == 'criar_conta' and resultado: # Para criação de conta
            nova_conta = resultado 
            cliente = nova_conta.cliente
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Transação: Criação de Conta | Conta: {nova_conta.numero} | Cliente: {cliente.nome}")
        return resultado
    return wrapper

class Transacao(ABC):
    def __init__(self, valor: float):
        self._valor = valor
        self._id = get_next_transaction_id()
        self._data = datetime.now()

    @abstractproperty
    def valor(self) -> float:
        pass

    @abstractproperty
    def id(self) -> int:
        pass

    @abstractproperty
    def data(self) -> datetime:
        pass

    @abstractmethod
    @log_transacao 
    def registrar(self, conta: 'Conta') -> bool:
        pass

class Deposito(Transacao):
    def __init__(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser positivo.")
        super().__init__(valor)

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def id(self) -> int:
        return self._id

    @property
    def data(self) -> datetime:
        return self._data

    def registrar(self, conta: 'Conta') -> bool:
        if conta.depositar(self.valor):
            return True
        return False

class Saque(Transacao):
    def __init__(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
        super().__init__(valor)

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def id(self) -> int:
        return self._id

    @property
    def data(self) -> datetime:
        return self._data

    def registrar(self, conta: 'Conta') -> bool:
        if conta.sacar(self.valor):
            return True
        return False

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self) -> list[Transacao]:
        return self._transacoes

    def adicionar_transacao(self, transacao: Transacao):
        self._transacoes.append(transacao)

    def gerar_relatorio(self):
        print("\n--- Extrato ---")
        if not self._transacoes:
            print("Nenhuma transação realizada.")
            return

        for transacao in self._transacoes:
            tipo = type(transacao).__name__
            print(f"Tipo: {tipo:<8} | Valor: R${transacao.valor:7.2f} | Data: {transacao.data.strftime('%d/%m/%Y %H:%M:%S')}")
        print("---------------")

    
    def transacoes_por_tipo(self, tipo_filtro: str = None):
        for transacao in self._transacoes:
            if tipo_filtro is None or type(transacao).__name__.lower() == tipo_filtro.lower():
                yield transacao

class Conta:
    _AGENCIA_PADRAO = "0001"

    def __init__(self, cliente: 'Cliente', numero: int):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = Conta._AGENCIA_PADRAO
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: 'Cliente', numero: int):
        return cls(cliente, numero)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def cliente(self) -> 'Cliente':
        return self._cliente

    @property
    def historico(self) -> Historico:
        return self._historico

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n!!! Operação falhou! O valor do saque deve ser positivo.")
            return False

        if valor > self._saldo:
            print("\n!!! Operação falhou! Saldo insuficiente.")
            return False

        self._saldo -= valor
        print(f"\nSaque de R${valor:.2f} realizado com sucesso.")
        return True

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n!!! Operação falhou! O valor do depósito deve ser positivo.")
            return False

        self._saldo += valor
        print(f"\nDepósito de R${valor:.2f} realizado com sucesso.")
        return True

class ContaCorrente(Conta):
    def __init__(self, cliente: 'Cliente', numero: int, limite_valor_saque: float = 500.0, limite_saques_diarios_cc: int = 3):
        super().__init__(cliente, numero)
        self._limite_valor_saque = limite_valor_saque
        self._limite_saques_diarios = limite_saques_diarios_cc
        self._saques_hoje = 0

    @property
    def limite(self) -> float:
        return self._limite_valor_saque

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n!!! Operação falhou! O valor do saque deve ser positivo.")
            return False

        if self._saques_hoje >= self._limite_saques_diarios:
            print("\n!!! Operação falhou! Limite de saques diários da Conta Corrente atingido.")
            return False

        if valor > self.limite:
            print(f"\n!!! Operação falhou! O valor do saque (R${valor:.2f}) excede o limite máximo por saque de R${self.limite:.2f}.")
            return False
            
        if valor > self._saldo:
            print("\n!!! Operação falhou! Saldo insuficiente.")
            return False

        self._saldo -= valor
        self._saques_hoje += 1
        print(f"\nSaque de R${valor:.2f} realizado com sucesso.")
        return True


class Cliente:
    def __init__(self, endereco: str):
        self._endereco = endereco
        self._contas = []

    @property
    def endereco(self) -> str:
        return self._endereco

    @property
    def contas(self) -> list['Conta']:
        return self._contas

    def realizar_transacao(self, conta: 'Conta', transacao: Transacao) -> bool:
        if conta not in self.contas:
            print("Erro: Conta não pertence a este cliente.")
            return False

        sucesso = transacao.registrar(conta)
        if sucesso:
            conta.historico.adicionar_transacao(transacao)
        return sucesso

    def adicionar_conta(self, conta: 'Conta'):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, data_nascimento: str, endereco: str):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def data_nascimento(self) -> str:
        return self._data_nascimento


class ContasIterator:
    def __init__(self, contas: list[Conta]):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._contas):
            conta = self._contas[self._index]
            self._index += 1
            
            cpf_cliente = conta.cliente.cpf if isinstance(conta.cliente, PessoaFisica) else "N/A"
            return {
                "numero": conta.numero,
                "agencia": conta.agencia,
                "saldo": conta.saldo,
                "cliente_nome": conta.cliente.nome,
                "cliente_cpf": cpf_cliente, 
                "tipo_conta": type(conta).__name__
            }
        else:
            raise StopIteration

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    print("\n" + "="*20 + " MENU " + "="*20)
    print("[d] Depositar")
    print("[s] Sacar")
    print("[e] Extrato")
    print("[nc] Nova conta")
    print("[lc] Listar contas")
    print("[nu] Novo usuário")
    print("[lt] Listar transações por tipo (gerador)") # Nova opção
    print("[q] Sair")
    print("="*46)
    return input("=> ").lower().strip()

def filtrar_cliente(cpf: str, clientes: list[PessoaFisica]) -> PessoaFisica | None:
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def recuperar_conta_cliente(cliente: Cliente, numero_conta: int) -> Conta | None:
    for conta in cliente.contas:
        if conta.numero == numero_conta:
            return conta
    return None

def cadastrar_usuario(clientes: list[PessoaFisica]):
    print("\n--- Novo Usuário ---")
    cpf = input("Informe o CPF (somente números): ")
    cliente_existente = filtrar_cliente(cpf, clientes)

    if cliente_existente:
        print("\n!!! Erro: Já existe um cliente com este CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    novo_cliente = PessoaFisica(cpf=cpf, nome=nome, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(novo_cliente)
    print("\n>>> Usuário criado com sucesso!")

@log_transacao 
def criar_conta(clientes: list[PessoaFisica], contas: list[Conta]):
    print("\n--- Criar Nova Conta ---")
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Erro: Cliente não encontrado, crie um novo usuário primeiro!")
        return None 

    novo_numero_conta = len(contas) + 1001

    try:
        limite_valor_saque_cc = float(input("Informe o limite MÁXIMO por saque (ex: 500): "))
        limite_saques_diarios_cc = int(input("Informe o limite de SAQUES DIÁRIOS (ex: 3): "))
        
        nova_conta = ContaCorrente(cliente=cliente, numero=novo_numero_conta, 
                                   limite_valor_saque=limite_valor_saque_cc, 
                                   limite_saques_diarios_cc=limite_saques_diarios_cc)
    except ValueError:
        print("\n!!! Erro: Valores de limite ou saques inválidos. Conta não criada.")
        return None 

    contas.append(nova_conta)
    cliente.adicionar_conta(nova_conta)
    print(f"\n>>> Conta {nova_conta.numero} (Conta Corrente) criada com sucesso para {cliente.nome}!")
    return nova_conta 


def listar_contas(contas: list[Conta]):
    print("\n--- Lista de Contas ---")
    if not contas:
        print("Nenhuma conta cadastrada.")
        return

    
    for conta_info in ContasIterator(contas):
        print(f"\nAgência:\t{conta_info['agencia']}")
        print(f"Conta:\t\t{conta_info['numero']}")
        print(f"Tipo:\t\t{conta_info['tipo_conta']}")
        print(f"Titular:\t{conta_info['cliente_nome']}")
        print(f"CPF:\t\t{conta_info['cliente_cpf']}") # Usando o CPF do iterador
        print(f"Saldo:\t\tR${conta_info['saldo']:.2f}")
        # Para o limite, acessamos diretamente a conta original pois não foi adicionado ao iterador para evitar complexidade desnecessária
        conta_original = next((c for c in contas if c.numero == conta_info['numero']), None)
        if isinstance(conta_original, ContaCorrente):
            print(f"Limite por Saque: R${conta_original.limite:.2f}")
            print(f"Limite Saques Diários: {conta_original._limite_saques_diarios}")
        print("-" * 30)


def depositar(clientes: list[PessoaFisica]):
    print("\n--- Depositar ---")
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Erro: Cliente não encontrado!")
        return

    if not cliente.contas:
        print("\n!!! Erro: Cliente não possui contas. Crie uma conta primeiro.")
        return

    print("\nContas disponíveis para depósito:")
    for i, conta in enumerate(cliente.contas):
        print(f"  [{i+1}] Conta: {conta.numero} - Saldo: R${conta.saldo:.2f} ({type(conta).__name__})")
    
    escolha_conta = input("Escolha o número da conta para depósito: ")
    try:
        idx_conta = int(escolha_conta) - 1
        if not (0 <= idx_conta < len(cliente.contas)):
            raise ValueError
        conta = cliente.contas[idx_conta]
    except ValueError:
        print("\n!!! Erro: Seleção de conta inválida.")
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
        if valor <= 0:
            raise ValueError
    except ValueError:
        print("\n!!! Erro: Valor de depósito inválido. Informe um número positivo.")
        return

    transacao = Deposito(valor)
    cliente.realizar_transacao(conta, transacao)
    print(f"Saldo atual da conta {conta.numero}: R${conta.saldo:.2f}")


def sacar(clientes: list[PessoaFisica]):
    print("\n--- Sacar ---")
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Erro: Cliente não encontrado!")
        return

    if not cliente.contas:
        print("\n!!! Erro: Cliente não possui contas. Crie uma conta primeiro.")
        return
    
    print("\nContas disponíveis para saque:")
    for i, conta in enumerate(cliente.contas):
        print(f"  [{i+1}] Conta: {conta.numero} - Saldo: R${conta.saldo:.2f} ({type(conta).__name__})")
    
    escolha_conta = input("Escolha o número da conta para saque: ")
    try:
        idx_conta = int(escolha_conta) - 1
        if not (0 <= idx_conta < len(cliente.contas)):
            raise ValueError
        conta = cliente.contas[idx_conta]
    except ValueError:
        print("\n!!! Erro: Seleção de conta inválida.")
        return

    try:
        valor = float(input("Informe o valor do saque: "))
    except ValueError:
        print("\n!!! Erro: Valor de saque inválido. Informe um número.")
        return

    transacao = Saque(valor)
    cliente.realizar_transacao(conta, transacao)
    print(f"Saldo atual da conta {conta.numero}: R${conta.saldo:.2f}")

def exibir_extrato(clientes: list[PessoaFisica]):
    print("\n--- Extrato ---")
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Erro: Cliente não encontrado!")
        return

    if not cliente.contas:
        print("\n!!! Erro: Cliente não possui contas.")
        return

    print("\nContas disponíveis para extrato:")
    for i, conta in enumerate(cliente.contas):
        print(f"  [{i+1}] Conta: {conta.numero} - Saldo: R${conta.saldo:.2f} ({type(conta).__name__})")
    
    escolha_conta = input("Escolha o número da conta para extrato: ")
    try:
        idx_conta = int(escolha_conta) - 1
        if not (0 <= idx_conta < len(cliente.contas)):
            raise ValueError
        conta = cliente.contas[idx_conta]
    except ValueError:
        print("\n!!! Erro: Seleção de conta inválida.")
        return

    conta.historico.gerar_relatorio()
    print(f"Saldo Atual: R${conta.saldo:.2f}")

def listar_transacoes_por_tipo(clientes: list[PessoaFisica]):
    print("\n--- Listar Transações por Tipo ---")
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Erro: Cliente não encontrado!")
        return

    if not cliente.contas:
        print("\n!!! Erro: Cliente não possui contas.")
        return
    
    print("\nContas disponíveis para listar transações:")
    for i, conta in enumerate(cliente.contas):
        print(f"  [{i+1}] Conta: {conta.numero} - Saldo: R${conta.saldo:.2f} ({type(conta).__name__})")
    
    escolha_conta = input("Escolha o número da conta: ")
    try:
        idx_conta = int(escolha_conta) - 1
        if not (0 <= idx_conta < len(cliente.contas)):
            raise ValueError
        conta = cliente.contas[idx_conta]
    except ValueError:
        print("\n!!! Erro: Seleção de conta inválida.")
        return

    tipo_filtro = input("Filtrar por tipo (Deposito/Saque) ou deixar em branco para todos: ").strip()
    
    print(f"\n--- Transações da Conta {conta.numero} (Filtrado por: {tipo_filtro if tipo_filtro else 'Todos'}) ---")
    encontrou_transacao = False
    for transacao in conta.historico.transacoes_por_tipo(tipo_filtro):
        tipo = type(transacao).__name__
        print(f"Tipo: {tipo:<8} | Valor: R${transacao.valor:7.2f} | Data: {transacao.data.strftime('%d/%m/%Y %H:%M:%S')}")
        encontrou_transacao = True
    
    if not encontrou_transacao:
        print("Nenhuma transação encontrada para o filtro especificado.")
    print("----------------------------------------------------------")


def main():
    clientes: list[PessoaFisica] = []
    contas: list[Conta] = []

    while True:
        limpar_tela()
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            cadastrar_usuario(clientes)
        elif opcao == "nc":
            nova_conta_criada = criar_conta(clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "lt": 
            listar_transacoes_por_tipo(clientes)
        elif opcao == "q":
            print("\nSaindo do sistema. Até mais!")
            break
        else:
            print("\n!!! Operação inválida, por favor selecione novamente a opção desejada.")

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()