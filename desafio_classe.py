
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __str__(self) -> str:
        return f"""
                Nome: {self.nome}
                Data de Nascimento: {self.data_nascimento}
                CPF: {self.cpf}
                Endereço: {self.endereco}
        """

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Não foi possivel realizar operação - SALDO INSUFICIENTE")

        elif valor > 0:
            self._saldo -= valor
            print(f"Saque no valor de R${valor:.2f} foi realizado com sucesso")
            return True

        else:
            print("Opção Inválida!!!!!!")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"Valor de R$ {valor:.2f} foi depositado com Sucesso!!\n")
        else:
            print(f"Depósito inválido!!! Valor de R${valor:.2f} não é válido\n")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("Atenção: Limite de transações foi atingido") 

        elif excedeu_saques:
            print("Atenção: Limite de Saque Diário Atingido") 

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)



def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):    

    if not cliente.contas:
        print("Não há nenhuma conta vinculado ao cliente informado")
        return
    
    return cliente.conta[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Não ha nenhum cliente cadastrado")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Não ha nenhum cliente cadastrado")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Não ha nenhum cliente cadastrado")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("CPF inválido - Usuário ja possui cadastro!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento: ")
    endereco = input("Informe o endereço: ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Não ha nenhum cliente cadastrado")

        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)    

    print(f"""Conta foi criada com Sucesso!!!
          
                Nome do Cliente: {cliente.nome}
                Agencia: {conta.agencia}
                Nº da Conta: {conta.numero}
          """)  

def listar_contas(contas):
    if not contas:
        print("   ","Não há contas cadastradas")
     
    else:
        for conta in contas:
            print(conta)
            print("   ","-"*68)
def listar_clientes(clientes):
    if not clientes:
        print("   ","Não há clientes cadastrados")
    else:
        for cliente in clientes:
            print (cliente)
            print("   ","-"*68)



logo = """
    ===================================================================
                            Vaz Bank
    ===================================================================
"""

menu_inicial = f"""
    {logo}
    Insira opção desejada:

    [a] Gerenciamento de Clientes e Contas
    [b] Operações Bancarias  
    [q] Sair              

=> """

menu_user = f"""
    {logo}
    Bem vindo ao Vaz Bank! Digite a letra correspondente para acessar serviço desejado:

    [d] Depositar
    [s] Sacar
    [e] Extrato
    [q] Sair

=> """

menu_admin = f"""
    {logo}
    Bem vindo ao Vaz Bank! Digite a letra correspondente para acessar serviço desejado:

    [u] Cadastrar Cliente
    [c] Criar Conta Corrente
    [p] Lista de Clientes
    [x] Lista de Contas
    [q] Sair

=> """


def main():
    clientes = []
    contas = []

    

    while True:

        opcao =input(menu_inicial).lower()

        if opcao == "b":
            while True:    

                opcao=input(menu_user).lower()

                if opcao == "d":   
                    depositar(clientes)                
                elif opcao == "s":
                    sacar(clientes)                
                elif opcao == "e":
                    exibir_extrato(clientes)
                elif opcao == "q":
                    break
                else:
                    print("Opção Inválida!!!!!!")

        elif opcao == "a":

            while True:

                opcao=input(menu_admin).lower()

                if opcao == "u":
                    criar_cliente(clientes)
                elif opcao == "c":
                    numero_conta = len(contas) + 1
                    criar_conta(numero_conta, clientes, contas)
                elif opcao == "p":
                    print(logo)
                    listar_clientes(clientes)                    
                elif opcao == "x": 
                    print(logo)               
                    listar_contas(contas)
                elif opcao == "q":
                    break
                else:
                    print("Opção Inválida!!!!!!")

        elif opcao == "q":
                    break
        else:
            print("Opção Inválida!!!!!!")


main()