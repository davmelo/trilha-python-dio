from abc import ABC, abstractmethod
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
    def __init__(self, *, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._extrato = Extrato()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def extrato(self):
        return self._extrato

    def sacar(self, valor):
        saldo = self._saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n ## Operação não realizada! Você não tem saldo suficiente. ##")
            return False
        
        elif valor > 0:
            self._saldo -= valor
            print("\n ## Saque realizado com sucesso. ##")
            return True
        
        else:
            print("\n ## Operação não realizada! O valor informado é inválido. ##")
            return False
        

    def depositar(self, valor):
        deposito_valido = valor > 0

        if deposito_valido:
            self._saldo += valor
            print("\n## Depósito realizado com sucesso. ##")
            return True
        
        else:
            print("\n## Operação não realizada! O valor informado é inválido. ##")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.extrato.transacoes if transacao['tipo'] == Saque.__name__])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques > self.limite_saques

        if excedeu_limite:
            print("\n ## Operação não realizada! O valor do saque excede o limite por operação.  ##")
            return False

        elif excedeu_saques:
            print("\n ## Operação não realizada! Limite de saques diários atingido. ##")
            return False
        
        else:
            return super().sacar(valor)

    def __str__(self):
        return f"\n     Agência: {self.agencia}\n     Conta: {self.numero}\n     Titular: {self.cliente.nome}"


class Extrato:
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
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )


class Transacao(ABC):
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
            conta.extrato.adicionar_transacao(self)
        

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.extrato.adicionar_transacao(self)


clientes_banco_python = []


def retornar_primeiro_nome(nome_completo):
    return nome_completo.split(" ")[0]

def exibir_extrato(conta):
    print("\n    ## EXTRATO ##")
    print(f"\n    {conta.cliente.nome} {conta.agencia} {conta.numero}\n")
    for transacao in conta.extrato.transacoes:
        tipo_transacao = "-" if transacao["tipo"] == "Saque" else "+"
        print(f"     Tipo: {transacao["tipo"]}\n     {tipo_transacao}R${transacao["valor"]:.2f}\t{transacao["data"]}")

    print(f"    Saldo: R${conta.saldo:.2f}")

def depositar(cliente):
    numero_conta = int(input(" Insira o número da conta onde será realizado o depósito: "))
    conta = procurar_conta(cliente, numero_conta)
    valor = float(input(" Insira o valor a ser depositado: "))
    deposito = Deposito(valor)
    cliente_encontrado.realizar_transacao(conta, deposito)

def sacar(cliente):
    numero_conta = int(input(" Insira o número da conta onde será realizado o saque: "))
    conta = procurar_conta(cliente, numero_conta)
    valor = float(input(" Insira o valor a ser sacado: "))
    saque = Saque(valor)
    cliente_encontrado.realizar_transacao(conta, saque)

def procurar_cliente(clientes, cpf):
    clientes_encontrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_encontrados[0] if clientes_encontrados else None

def procurar_conta(cliente, numero=1):
    contas_encontradas = [conta for conta in cliente.contas if conta.numero == numero]
    return contas_encontradas[0] if contas_encontradas else None

def ler_dados_cliente():
    nome = str(input(" Digite o seu nome: "))
    data_nascimento = str(input(" Digite sua data de nascimento (dd/mm/aa): "))
    logradouro  = str(input(" Digite seu logradouro: "))
    numero_casa  = str(input(" Digite o número da casa: "))
    bairro  = str(input(" Digite seu bairro: "))
    cidade_estado  = str(input(" Digite sua cidade e estado (ex.: Recife/PE): "))
    endereco = f"{logradouro}, {numero_casa} - {bairro} - {cidade_estado}"
    
    return {"nome": nome, "data_nascimento": data_nascimento, "endereco": endereco}

def cadastrar_cliente(clientes, cpf):
    dados_cliente = ler_dados_cliente()
    cliente = PessoaFisica(cpf=cpf, nome=dados_cliente["nome"],
                            data_nascimento=dados_cliente["data_nascimento"],
                            endereco=dados_cliente["endereco"])
    clientes.append(cliente)
    print("\n Cadastro realizado com sucesso! Você já pode usufurir dos benefícios do Banco Python.")

def total_contas_criadas(clientes):
    return sum([len(cliente.contas) for cliente in clientes]) + 1

def criar_conta_corrente(cliente, numero_da_conta):
    conta_corrente = ContaCorrente(cliente=cliente, numero=numero_da_conta)
    cliente.adicionar_conta(conta_corrente)
    print(f"\n    Parabéns, sua conta foi criada com sucesso.\n{conta_corrente}")

def mensagem_nao_possui_conta(nome_completo):
    nome = retornar_primeiro_nome(nome_completo)
    print(f"\n Sr(a) {nome}, você ainda não possui uma conta em nosso banco. Crie uma antes de realizar alguma movimentação.")

def mensagem_nao_cliente():
    print("\n Você ainda não é cliente do Banco Python. Cadastre-se antes de criar uma conta.")

def percorrer_contas(contas):
    for conta in contas:
        print("\n  Você ainda não fez movimentações nessa conta") if not conta.transacoes else exibir_extrato(conta)

menu = """ 
 Selecione um opção:
 [d] Depositar
 [s] Sacar
 [e] Extrato
 [u] Cadastrar cliente
 [c] Criar conta corrente
 [q] Sair

 -> """

print("<-> BEM-VIND@ AO BANCO PYTHON <->")

while True:
    opcao = input(menu).strip().lower()

    if opcao == 'd':
        cpf = str(input("\n Insira seu CPF: "))
        cliente_encontrado = procurar_cliente(clientes_banco_python, cpf)
        possui_conta = cliente_encontrado.contas if cliente_encontrado else None

        if not cliente_encontrado:
            mensagem_nao_cliente()

        elif not possui_conta:
            mensagem_nao_possui_conta(cliente_encontrado.nome)

        else:
            #FIXME ocorre um erro se informa um número de conta não válido
            depositar(cliente_encontrado)

    elif opcao == 's':
        cpf = str(input("\n Insira seu CPF: "))
        cliente_encontrado = procurar_cliente(clientes_banco_python, cpf)
        possui_conta = cliente_encontrado.contas if cliente_encontrado else None

        if not cliente_encontrado:
            mensagem_nao_cliente()

        elif not possui_conta:
            mensagem_nao_possui_conta(cliente_encontrado.nome)

        else:
            #FIXME ocorre um erro se informa um número de conta não válido
            sacar(cliente_encontrado)

    elif opcao == 'e':
        cpf = str(input("\n Insira seu CPF: "))
        cliente_encontrado = procurar_cliente(clientes_banco_python, cpf)
        possui_conta = cliente_encontrado.contas if cliente_encontrado else None

        if not cliente_encontrado:
            mensagem_nao_cliente()

        elif not possui_conta:
            mensagem_nao_possui_conta(cliente_encontrado.nome)
        
        else:
            if len(possui_conta) > 1:
                
                menu_extrato = "\n Como deseja fazer?\n [u] Extrato de uma conta\n [t] Extrato de todas as contas\n -> "
                opcao_extrato = str(input(menu_extrato)).strip().lower()

                if opcao_extrato == 'u':
                    numero_conta = int(input(" Insira o número da conta: "))
                    conta = procurar_conta(cliente_encontrado, numero_conta)
                    print("\n  Você ainda não fez movimentações nessa conta") if not conta.extrato.transacoes else exibir_extrato(conta)

                elif opcao_extrato == 't':
                    percorrer_contas(cliente_encontrado.contas)

                else:
                    pass

            else:                
                print("\n  Você ainda não fez movimentações nessa conta") if not possui_conta[0].extrato.transacoes else exibir_extrato(possui_conta[0])

    elif opcao == 'u':
        cpf = str(input("\n Insira seu CPF: "))
        cliente_encontrado = procurar_cliente(clientes_banco_python, cpf)

        if not cliente_encontrado:
            cadastrar_cliente(clientes_banco_python, cpf)

        else:
            nome = retornar_primeiro_nome(cliente_encontrado.nome)
            print(f"\n Olá, {nome}. Você já é cliente do Banco Python, bem-vind@ de volta!")

    elif opcao == 'c':
        cpf = str(input("\n Insira seu CPF: "))
        cliente_encontrado = procurar_cliente(clientes_banco_python, cpf)
        numero_de_contas = total_contas_criadas(clientes_banco_python)
        
        if cliente_encontrado:
            criar_conta_corrente(cliente_encontrado, numero_de_contas)

        else:
            mensagem_nao_cliente()

    elif opcao == 'q':
        print("Encerrando sessão...")
        break

    else:
        print("Selecione uma opção válida!")