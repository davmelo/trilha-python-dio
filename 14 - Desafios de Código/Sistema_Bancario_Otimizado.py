LIMITE_DE_SAQUES = 3
LIMITE_POR_SAQUE = 500

menu = '''

 QUAL OPERAÇÃO DESEJA REALIZAR?

 [d] Depositar
 [s] Sacar
 [e] Extrato
 [u] Cadastrar usuário
 [c] Cadastrar conta corrente
 [q] Sair

 -> '''

contas_banco = []
usuarios_banco = []

def procurar_usuario(cpf):
    for i in range(len(usuarios_banco)):
        if cpf in usuarios_banco[i].keys():
            return usuarios_banco[i]
    
    return {}

def procurar_conta(cpf):
    for i in range(len(contas_banco)):
        if cpf in contas_banco[i].keys():
            return i+1
    
    return 0

def ler_dados_usuario():
    nome = str(input("Digite o seu nome: "))
    data_nascimento = str(input("Digite sua data de nascimento (dd/mm/aa): "))
    logradouro  = str(input("Digite seu logradouro: "))
    numero_casa  = str(input("Digite o número da casa: "))
    bairro  = str(input("Digite seu bairro: "))
    cidade_estado  = str(input("Digite sua cidade e estado (ex.: Recife/PE): "))
    endereco = f"{logradouro}, {numero_casa} - {bairro} - {cidade_estado}"
    
    return nome, data_nascimento, endereco

def cadastrar_usuario(cpf, nome, data_nascimento, endereco):
    usuario = {}
    usuario[cpf] = {"nome": nome, "data_nascimento": data_nascimento, "endereco": endereco}
    usuarios_banco.append(usuario)

def cadastrar_conta(cpf):
    numero_conta = str(len(contas_banco) + 1)

    usuario_com_conta = procurar_conta(cpf)

    conta_criada = {}
    saldo = 0
    extrato = ""

    if not usuario_com_conta:
        conta_criada[cpf] = [{"agencia_conta": ("0001", numero_conta), "saldo": saldo, "extrato": extrato, "numero_saques": 0}]
        contas_banco.append(conta_criada)
        return conta_criada[cpf][0]["agencia_conta"]
    else:
        conta_criada = {"agencia_conta": ("0001", numero_conta), "saldo": saldo, "extrato": extrato, "numero_saques": 0}
        contas_banco[usuario_com_conta - 1][cpf].append(conta_criada)
        return conta_criada["agencia_conta"]

def depositar(cpf, agencia_conta, deposito, indice_conta, /):

    for conta in contas_banco[indice_conta - 1][cpf]:
        if agencia_conta in conta.values():
            conta['saldo'] += deposito
            conta['extrato'] += f"    Depósito de R$ {deposito:.2f}\n"
            pass

def sacar(*, cpf, agencia_conta, saque, indice_conta):
    for conta in contas_banco[indice_conta - 1][cpf]:
        if agencia_conta in conta.values():
            if conta["numero_saques"] == LIMITE_DE_SAQUES:
                print("Você atingiu seu limite de saques diários. Tente novamente amanhã.")
            else:
                if conta["saldo"] < saque:
                    print("Valor do saque excede seu saldo. Saque um valor menor")
                else:
                    conta["saldo"] -= saque   
                    conta['extrato'] += f"    Saque de R$ {saque:.2f}\n"
                    conta["numero_saques"] += 1
                    pass

def exibir_extrato(usuario, cpf, indice_conta):

    print("<---<--<-< Extrato Bancário >->-->--->")
    print(f"\nNome: {usuario[cpf]["nome"]}")
    print("Contas: ")
    
    for conta in contas_banco[indice_conta - 1][cpf]:
        print(f"   Angêcia: {conta["agencia_conta"][0]}")
        print(f"   Conta: {conta["agencia_conta"][1]}")
        print(conta["extrato"])
        print(f"    Saldo: R$ {conta["saldo"]:.2f}\n")

    print("<-----<----<---< ---- >--->---->----->")

def verificar_cadastro_banco_conta(cpf):
    usuario = procurar_usuario(cpf)
    usuario_com_conta = procurar_conta(cpf)
    if not usuario:
        print("Você ainda não tem cadastro em nosso banco. Cadastre-se antes de fazer movimentações.")
        return 0, 0
    elif not usuario_com_conta:
        print("Você ainda não tem uma conta cadastrada. Crie uma conta antes de fazer movimentações.")
        return 0, 0
    else:
        return usuario, usuario_com_conta


while True:
    opcao = input(menu)

    if opcao == 'd':
        cpf = str(input("\nDigite o CPF do titular da conta: "))

        usuario, usuario_com_conta = verificar_cadastro_banco_conta(cpf)
        if not usuario and not usuario_com_conta:
            pass
        
        else:
            numero_conta = str(input("Digite o número da conta: "))
            agencia_conta = ("0001", numero_conta)
            deposito = int(input("Insira o valor do depósito: "))
            depositar(cpf, agencia_conta, deposito, usuario_com_conta)
            print("Depósito realizado com sucesso!")
        
    elif opcao == 's':
        cpf = str(input("\nDigite o CPF do titular da conta: "))

        usuario, usuario_com_conta = verificar_cadastro_banco_conta(cpf)
        if not usuario and not usuario_com_conta:
            pass
        
        else:
            numero_conta = str(input("Digite o número da conta: "))
            agencia_conta = ("0001", numero_conta)
            saque = int(input("Insira o valor do saque: "))
            if saque > LIMITE_POR_SAQUE:
                print("Valor do saque acima do limite permitido (R$ 500.00). Tente um valor menor.")
            else:
                sacar(cpf=cpf, agencia_conta=agencia_conta, saque=saque, indice_conta=usuario_com_conta)
                print("Saque realizado com sucesso!")

    elif opcao == 'e':
        cpf = str(input("\nDigite o CPF do titular da conta: "))

        usuario, usuario_com_conta = verificar_cadastro_banco_conta(cpf)
        if not usuario and not usuario_com_conta:
            pass
        
        else:
            exibir_extrato(usuario, cpf, usuario_com_conta)

    elif opcao == 'u':
        cpf = str(input("\nDigite o seu CPF: "))

        usuario = procurar_usuario(cpf)
        if not usuario:
            nome, data_nascimento, endereco = ler_dados_usuario()
            cadastrar_usuario(cpf, nome, data_nascimento, endereco)
            print(f"\nCadastro realizado. Seja bem-vindo, {nome.split(" ")[0]}!")
        
        else:
            print(f"\nOlá, {usuario[cpf]["nome"].split(" ")[0]}, você já está cadastrado em nosso banco. Seja bem-vindo de volta!")
            
    elif opcao == 'c':
        cpf = str(input("\nQual o CPF do titula da conta: "))

        usuario = procurar_usuario(cpf)
        if not usuario:
            print("Você ainda não tem cadastro em nosso banco. Cadastre-se antes de criar uma conta.")

        else:
            agencia_conta = cadastrar_conta(cpf)
            print(f"Conta criada com sucesso. Você já pode começar a fazer suas transações.\nAgência: {agencia_conta[0]} Conta: {agencia_conta[1]}")

    elif opcao == 'q':
        print("Ecerrando sessão...")
        break

    else:
        print("Opção inválida!")