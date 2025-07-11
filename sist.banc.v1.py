menu = '''
[d] Depositar 
[s] Sacar
[e] Extrato
[q] Sair    

'''

saldo = 0 
limite = 500
extrato = ""
numero_saques = 0
limite_saques = 3

while True:

    opcao = input(menu)

    if opcao == 'd':
        valor = float(input('Informe o valor do depósito: '))


        if valor > 0:
            saldo += valor 
            extrato += f'Depósito: R$ {valor:.2f}\n'

        else:
            print('A operação de depósito falhou. Valor informado inválido')
    
    elif opcao == 's':
        valor = float(input('Informe o valor de saque: '))


        if valor > saldo:
            print('A operação de saque falhou. Saldo insuficiente')
        
        elif valor > limite:
            print('A operação de saque falhou. O valor solicitado ultrapassa o seu limite')

        elif numero_saques >= limite_saques:
            print('A operação falhou. O número limite de saques foi excedido')

        elif valor > 0:
            saldo -= valor
            extrato += f'Saque: R$ {valor:.2f}\n'
        else:
            print('A operação de depósito falhou. Valor informado inválido')
    
    elif opcao == 'e':
        print('\n========== EXTRAT0 ==========')
        print('Não foram realizadas movimentações.' if not extrato else extrato)
        print(f'\nSaldo: R$ {saldo:.2f}')
        print('\n=============================')
    
    elif opcao == 'q':
        break

    else:
        print('Operação inválida. Selecione novamente algumas das opções do menu')