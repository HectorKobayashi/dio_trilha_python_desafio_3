import re
from abc import ABC, abstractmethod, abstractproperty

class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, **kw):
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento
        super().__init__(**kw)
        self._contas = []
    
    def adicionar_conta(self, conta):
        self._contas.append(conta)

    @property
    def contas(self):
        return self._contas
    

    def __str__(self):
        return f"{self.__class__.__name__}: {', '.join([f'{chave}={valor}' for chave, valor in self.__dict__.items()])}"



class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo" : transacao.__class__.__name__, 
                "valor" : transacao.valor
            }
        )


class Conta:
    def __init__(self, cliente, numero):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
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
    

    def __str__(self):
        return f"{self.__class__.__name__}: {', '.join([f'{chave}={valor}' for chave, valor in self.__dict__.items()])}"

    
    def nova_conta(cliente, numero):
        return ContaCorrente(cliente=cliente, numero=numero)
    
        
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Deposito realizado")
            return True

        else:
            print("Operação falhou! O valor informado é inválido.")
            return False
        
    def mostrar_transacoes (self):
        print("\n================ EXTRATO ================")
        if not self._historico.transacoes :
            print("Não foram realizadas movimentações.")
        else:
            for transacao in self._historico.transacoes:
                tipo = transacao.get("tipo")
                valor = transacao.get("valor")
                print("\n==========")
                print(f"\nTipo:{tipo}")
                print(f"\nValor:{valor}")
        print("\n==========########==========")
        print(f"\nSaldo: R$ {self._saldo:.2f}")
        print("==========================================")
    
    
        

class ContaCorrente (Conta):
    def __init__(self, **kw):
        self._limite = 500.0
        self._limite_saques = 3
        super().__init__(**kw)
    
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

    @property
    def limite(self):
        return self._limite

    @property
    def limite_saques(self):
        return self._limite_saques

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self._historico.transacoes if transacao["tipo"] == Saque.__name__ ]
        )
        excedeu_saldo = valor > self._saldo
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_saldo:
            print("Operação falhou! Você não tem saldo suficiente.")
            return False

        elif excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")
            return False

        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")
            return False

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado")
            return True

        else:
            print("Operação falhou! O valor informado é inválido.")
            return False

  

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor, **kw):
        self._valor = valor
        super().__init__(**kw)
        
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor, **kw):
        self._valor = valor
        super().__init__(**kw)
        
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            
       
menu = """

[d] Depositar
[s] Sacar
[e] Extrato
[u] Cadastrar Cliente
[c] Cadastrar Conta 
[l] Listar Contas
[q] Sair

=> """


def listar_contas(lista_conta):
    for conta in lista_conta:
        linha = f"""\
            Agência:\t{conta['agencia']}
            Número da Conta:\t\t{conta['numero_conta']}
            Titular:\t{conta['cpf']}
        """
    print(linha)
    print("==========================================")


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente._cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente, numero_conta):

    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    else:
        for conta in cliente.contas:
            if int(numero_conta) == int(conta.numero):
                return conta
        
    print("\n@@@ Cliente não possui a conta informada! @@@")
    return 


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    numero_conta = input("informe o numero da conta: ")
    conta = recuperar_conta_cliente(cliente, numero_conta)
    if not conta:
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    cliente.realizar_transacao(conta, transacao)



def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    numero_conta = input("informe o numero da conta: ")
    conta = recuperar_conta_cliente(cliente, numero_conta)
    if not conta:
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    cliente.realizar_transacao(conta, transacao)


def extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    numero_conta = input("informe o numero da conta: ")
    conta = recuperar_conta_cliente(cliente, numero_conta)
    if not conta:
        return
    
    conta.mostrar_transacoes()

    return


def criar_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n Já existe um cliente com este cpf")
        return

    nome = input("Informe o nome: ")
    data_nascimento = input("Informe a data de nascimento: ")
    endereco = input("Informe o endereco: ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    return
    

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = Conta.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print(f"Conta criada com sucesso")
    return



def main():
    clientes = []
    contas = []

    while True:
        opcao = input(menu)

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            extrato(clientes)

        elif opcao == "u":
            criar_cliente(clientes)

        elif opcao == "c":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


main()
