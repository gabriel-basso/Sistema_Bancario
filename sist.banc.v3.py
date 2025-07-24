from abc import ABC, abstractmethod
from datetime import datetime, timezone
import textwrap
from pathlib import Path

ROOT_PATH = Path(__file__).parent

class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f'''
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        '''
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1

class Cliente:
    def __init__(self, endereco):
        self.endereco= endereco
        self.contas= []
        self.indice_conta = 0

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print('\nErro. Número de transações diárias excedido')
            return

        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __repr__(self):
        return f"<PessoaFisica: ('{self.nome}', '{self.cpf}')>"

class Conta:    
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico() 

    @classmethod
    def nova_conta(cls, numero, cliente):
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
    
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 1000, limite_saques = 3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__])
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print(f'A operação de saque falhou. Limite excedido\n Limite de saque: R$ {self.limite}')
        elif excedeu_saques:
            print('A operação de saque falhou. Número máximo de saques atingido')
        else:
            return super().sacar(valor)
        return False
    
    def __repr__(self):
        return f"<ContaCorrente: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

    def __str__(self):
        return (
            f'Agência:\t {self.agencia}\n'
            f'C/C:\t {self.numero}\n'
            f'Titular:\t {self.cliente.nome}'     
        )

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,
                'data': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            }
        )

    def gerar_relatorio(self, tipo_transacao= None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao['tipo'].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self):
        data_atual = datetime.now(timezone.utc).date()
        transacoes = []
        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao['data'], '%d-%m-%Y %H:%M:%S').date()
            if data_atual == data_transacao:
                transacoes.append(transacao)
        return transacoes

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

# Decorador de log personalizado
def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        #Personalização para criar_cliente e criar_conta
        if func.__name__ == "criar_cliente":
            #O novo cliente é o último da lista, se foi criado
            if args and args[0] and isinstance(args[0][-1], PessoaFisica):
                cliente = args[0][-1]
                log_args = f"nome={cliente.nome}, cpf={cliente.cpf}"
            else:
                log_args = "nenhum cliente criado"
        elif func.__name__ == "criar_conta":
            #A nova conta é a última da lista, se foi criada
            if len(args) > 2 and args[2] and isinstance(args[2][-1], ContaCorrente):
                conta = args[2][-1]
                log_args = f"agencia={conta.agencia}"
            else:
                log_args = "nenhuma conta criada"
        else:
            log_args = f"args={args}, kwargs={kwargs}"

        with open(ROOT_PATH / 'log.txt', 'a', encoding='utf-8') as arquivo:
            arquivo.write(
                f"[{data_hora}] Função '{func.__name__}' executada com argumentos {log_args}. Retornou {resultado}\n"
            )
        return resultado
    return envelope

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
    return input(textwrap.dedent(menu_text))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados= [cliente for cliente in clientes if cliente.cpf == cpf ]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('Erro. O cliente não possui conta')
        return 
    return cliente.contas[0]

@log_transacao
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

@log_transacao
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

@log_transacao
def extrato(clientes):
    cpf = input('Informe o cpf do cliente (somente números): ')
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Usuário não encontrado")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    print('\n========== EXTRATO ==========')
    extrato = ''
    tem_transacao = False
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True 
        extrato += f"\n{transacao['data']}\n{transacao['tipo']:<10}: R$ {transacao['valor']:>8.2f}\n"
    if not tem_transacao:
        extrato = 'Não foram realizadas movimentações'
    print(extrato)
    print(f'\nSaldo:\tR$ {conta.saldo:.2f}')
    print('=============================')

@log_transacao
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

@log_transacao
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
    for conta in ContasIterador(contas):
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