menu = '''

 QUAL OPERAÇÃO DESEJA REALIZAR?

 [d] Depositar
 [s] Sacar
 [e] Extrato
 [q] Sair

 -> '''

saldo = 0
extrato = ""
numeros_saques = 0
LIMITE_DE_SAQUES = 3
LIMITE_POR_SAQUE = 500

while True:
    opcao = input(menu)

    if opcao == 's':
        if saldo == 0:
            print("Operação não realizada! Saldo insuficiente.")
        elif numeros_saques == LIMITE_DE_SAQUES:
            print("Operação não realizada! Você atingiu o limite de saques diários, tente novamente amanhã.")
        else:
            saque = float(input("Insira o valor do saque: "))
            excedeu_saldo = saque > saldo
            excedeu_limite = saque > LIMITE_POR_SAQUE
            valor_nao_valido = saque < 0

            if excedeu_saldo:
                print("Operação não realizada! Saldo insuficiente.")
            elif excedeu_limite:
                print(f"Operação não realizada! Valor acima do limite por saque (R$ {LIMITE_POR_SAQUE}.00).")
            elif valor_nao_valido:
                print("Operação não realizada! Insira um valor de saque válido.")
            else:
                saldo -= saque
                extrato += f"Saque de R$ {saque:.2f}\n"
                numeros_saques += 1
                print("Operação realizada! Retire as cédulas.")

    elif opcao == 'd':
        deposito = float(input("Insira o valor do depósito: "))
        if deposito > 0:
            saldo += deposito
            extrato += f"Depósito de R$ {deposito:.2f}\n"
            print("Depósito realizado com sucesso.")
        else:
             print("Operação não realizada! Insira um valor de depósito válido.")
        
    elif opcao == 'e':
        print("=============== EXTRATO BANCÁRIO ===============")
        print("Não foram realizadas movimentações." if not extrato else extrato)
        print(f"Saldo R$ {saldo:.2f}")

    elif opcao == 'q':
        print("Finalizando seção...")
        break

    else:
        print("Opção inválida!")