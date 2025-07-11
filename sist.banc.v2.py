def menu():
    menu = '''\n
    ========== MENU ==========
    [nu] Novo usuário
    [na] Nova conta
    [lc] Listar contas
    [d] Depositar
    [s] Sacar
    [e] Exibir extrato
    [q] Sair
    ==========================
    => '''

    return input(menu)

def depositar(saldo, valor, extrato):
    if valor > 0:
        saldo += valor
        extrato += f'Depósito: R$ {valor:.2f}\n'
        print('Depósito realizado com sucesso')
    else:
        print('A operação falhou. Insira um valor de depósito válido')

    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques > limite_saques

    if excedeu_saldo:
        print(f'A operação de saque falhou. Saldo insuficiente\n Saldo: R$ {saldo:.2f}')
    
    elif excedeu_limite:
        print(f'A operação de saque falhou. Limite excedido\n Limite de saque: R$ {limite}')
    
    elif excedeu_saques:
        print('A operação de saque falhou. Número máximo de saques atingido')

    elif valor > 0:
        saldo -= valor
        extrato += f'Saque: R$ {valor:.2f}\n'
        numero_saques += 1
        print('Saque realizado com êxito' )
    
    else:
        print('A operação falhou. Valor informado inválido.')

    return saldo, extrato

def exibir_extrato(saldo, /, *, extrato):
    print('========== EXTRATO ==========')
    print('Não foram realizadas movimentações' if not extrato else extrato)
    print(f'Saldo: R$ {saldo:.2f}')
    print('=============================')

def criar_usuarios(usuarios):
    cpf = input('Insira o CPF (somente números): ')
    usuario = filtrar_usuarios(cpf, usuarios)

    if usuario:
        print('Usuário ja existente')
        return
    
    nome = input('Informe o nome completo: ')
    data_nascimento = input('Informe a data de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço no formato (logradouro, nmro - cidade/sigla estado): ')
    usuarios.append({'Nome': nome, 'Data de nascimento': data_nascimento, 'CPF': cpf, 'Endereço': endereco})
    print('Usuário criado com sucesso')

def filtrar_usuarios(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario['CPF'] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(agencia, numero_conta, usuarios):
    cpf = input('Informe o CPF do usuario (somente números): ')
    usuario = filtrar_usuarios(cpf, usuarios)

    if usuario:
        print("Conta criada com sucesso")
        return ({'Agência': agencia, 'Número da conta': numero_conta, 'Usuário': usuario})
    
    print('Usuário não encontrado. Fluxo de criação de conta encerrado')

def listar_contas(contas):
    for conta in contas:
        linha = f'''
        Agência: {conta['Agência']}
        C/C: {conta['Número da conta']}
        Titular: {conta['Usuário']}
        '''

        print('=' * 100)
        print(linha)

def main():
    limite_saques = 3
    agencia = '0001'

    saldo = 0
    limite = 500
    extrato = ''
    numero_saques = 0
    usuarios = []
    contas = []

    while True:

        opcao = menu()

        if opcao == 'd':
            valor = float(input('Informe o valor do depósito: '))

            saldo, extrato = depositar(saldo, valor, extrato)

        elif opcao == 's':
            valor = float(input('Informe o valor de saque: '))

            saldo, extrato = sacar(
                saldo= saldo, 
                valor= valor,
                extrato= extrato,
                limite= limite,
                numero_saques= numero_saques, 
                limite_saques= limite_saques
            )
            
        elif opcao == 'e':
            exibir_extrato(saldo, extrato= extrato)

        elif opcao == 'nu':
            criar_usuarios(usuarios)

        elif opcao == 'na':
            numero_conta = len(contas) + 1
            conta = criar_conta(agencia, numero_conta, usuarios)

            if conta:
                contas.append(conta)

        elif opcao == 'lc':
            listar_contas(contas)

        elif opcao == 'q':
            break

        else:
            print('Operação inválida. Selecione novamente algumas das opções do menu')

main()