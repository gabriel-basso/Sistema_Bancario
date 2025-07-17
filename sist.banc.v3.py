from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco= endereco
        self.contas= []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco) #chamar construtor da classe pai
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:    
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico() 

    @classmethod #permite criar uma nova conta usando Conta.nova_conta(numero, cliente)
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente) #cls representa a própria classe que retorna uma nova instância da classe Conta.
    
    @property #Método utilizado para acessar atributos protegidos (_) 
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
            print(f'A operação de saque falhou. Saldo insuficiente\nSaldo:\t R$ {self.saldo:.2f}')
        
        elif valor > 0:
            self._saldo -= valor 
            print(f'Saque realizado com sucesso\nSaldo:\t R$ {self.saldo:.2f}')
            
            return True
        
        else:
            print('A operação de saque falhou. Valor informado inválido.')

            return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f'Depósito realizado com sucesso\nSaldo:\t R${self.saldo:.2f}')
        else:
            print('A operação falhou. Insira um valor de depósito válido')
            
            return False
        
        return True
    
#Aqui são definidas algumas das principais funções, como saque e deposito. Usando como estratégia o conceito de herança da classe Conta 
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 1000, limite_saques = 3):
        super().__init__(numero, cliente) #chamando contrutor e atributos da classe Conta
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__]) #list comprehension para verificar se o tipo de transação é igual a saque
        
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print(f'A operação de saque falhou. Limite excedido\n Limite de saque: R$ {self.limite}')
        
        elif excedeu_saques:
            print('A operação de saque falhou. Número máximo de saques atingido')
        
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return (
            f'Agência:\t {self.agencia}\n'
            f'C/C:\t {self.numero}\n'
            f'Titular:\t {self.cliente.nome}'     
        )

class Historico:
    def __init__(self):
        self._transacoes = [] #armazenar as transações em uma lista

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,
                'data': datetime.now().strftime('%d-%m-%Y %H:%M:%S'), #importado do modulo datetime 
            }
        )

#Classes abstratas 
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
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

#Functions para a function main()

def menu():
    menu_text = '''\n
    ========== MENU ==========
    [nu]\tNovo usuário
    [na]\tNova conta
    [lc]\tListar contas
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [q]\tSair
    ==========================
    => '''
    return input(textwrap.dedent(menu_text)) #Formatação de exibição

def filtrar_cliente(cpf, clientes):
    clientes_filtrados= [cliente for cliente in clientes if cliente.cpf == cpf ]

    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):

    if not cliente.contas:
        print('Erro. O cliente não possui conta')
        return 
    
    return cliente.contas[0]

def depositar(clientes):
    cpf = input('Informe o cpf do cliente (somente números): ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado')
        return
    
    valor = float(input('Informe o valor do depósito: '))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return 
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input('Informe o cpf do cliente (somente números): ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado')
        return
    
    valor = float(input('Informe o valor de saque: '))
    transacao = Saque(valor)
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def extrato(clientes):
    cpf = input('Informe o cpf do cliente (somente números): ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Usuário não encontrado")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print('\n ========== EXTRATO ==========')
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = 'Não foram realizadas movimentações'
    
    else:
        for transacao in transacoes:
            extrato += f"{transacao['tipo']:<10}: R$ {transacao['valor']:>8.2f}\n"
    print(extrato)
    print(f'\nSaldo:\tR$ {conta.saldo:.2f}')
    print('=============================')

def criar_cliente(clientes):
    cpf = input('Informe o cpf (somente números): ')
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print('Já existe um usuário com o número de cpf informado')
        return
    
    nome = input('Informe seu nome completo: ')
    data_nascimento = input('Informe sua data de nascimento no formato (dd-mm-aaaa): ')
    endereco = input('Informe seu endereco (Logradouro, Número - Cidade/Sigla estado): ')

    cliente = PessoaFisica(nome= nome, data_nascimento= data_nascimento, cpf= cpf, endereco= endereco)

    clientes.append(cliente)
    print('Usúario criado com sucesso. Seja bem-vindo ao time')

def criar_conta(numero_conta, clientes, contas):
    cpf = input('Informe o cpf (somente números): ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Usuário não encontrado. Encerrando o fluxo de criação de conta')
        return

    conta = ContaCorrente.nova_conta(cliente= cliente, numero= numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('Conta criada com sucesso')

def listar_contas(contas):

    for conta in contas:
        print('=' * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()
        if opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "na":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == 'd':
            depositar(clientes)

        elif opcao == 's':
            sacar(clientes)
        
        elif opcao == 'e':
            extrato(clientes)
        
        elif opcao == 'q':
            break

        else:
            print('Erro. Selecione uma opção válida')

main()
