from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class ContaIterador:
    def __init__(self, contas):
        self.contas = contas
        self.contador = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            conta = self.contas[self.contador]
            return conta
        except IndexError:
            raise StopIteration
        finally:
            self.contador += 1


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if len(conta.extrato.transacoes_do_dia()) >= 10:
            console.print("[red]Operação não realizada! Limite de operações diárias atingido.[/red]")

        else:
            transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, *, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.nome}')>"


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._extrato = Extrato()

    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)
    
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
            console.print("[red]Operação não realizada! Você não tem saldo suficiente.[/red]")
            return False
        
        elif valor > 0:
            self._saldo -= valor
            console.print("\n[cyan]Saque realizado com sucesso.[/cyan]")
            return True
        
        else:
            console.print("[red]Operação não realizada! O valor informado é inválido.[/red]")
            return False
        

    def depositar(self, valor):
        deposito_valido = valor > 0

        if deposito_valido:
            self._saldo += valor
            console.print("\n[cyan]Depósito realizado com sucesso.[/cyan]")
            return True
        
        else:
            console.print("[red]Operação não realizada! O valor informado é inválido.[/red]")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, numero, cliente, limite=500, limite_saques=3):
        return cls(numero, cliente, limite, limite_saques)


    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.extrato.transacoes if transacao['tipo'] == Saque.__name__])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            console.print("[red]Operação não realizada! O valor do saque excede o limite por operação.[/red]")
            return False

        elif excedeu_saques:
            console.print("[red]Operação não realizada! Limite de saques diários atingido.[/red]")
            return False
        
        else:
            return super().sacar(valor)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"


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
                "data": datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
            }
        )

    def transacoes_do_dia(self):
        data_atual = datetime.now(timezone.utc).date()
        transacoes = []

        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d-%m-%Y %H:%M:%S").date()
            if data_transacao == data_atual:
                transacoes.append(transacao)

        return transacoes

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao == None or transacao['tipo'].lower() == tipo_transacao.lower():
                yield transacao

            else:
                console.print("[red]Selecione uma opção válida.[/red]")


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

# OPERAÇÕES DE MANIPULAÇOES DE ARQUIVO
ROOT_PATH = Path(__file__).parent
def log_operacoes(funcao):
    def envelope(*args, **kwargs):
        resultado = funcao(*args, **kwargs)
        data_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        with open(ROOT_PATH / "log.txt", "a", encoding="utf-8") as arquivo_log: 
            arquivo_log.write(
                f"[{data_hora}] Função '{funcao.__name__}' executada com os argumentos {args} e {kwargs}. "
                f"Retornou {resultado}\n"
            )
        return resultado

    return envelope



# FUNÇÕES AUXILIARES
def retornar_primeiro_nome(nome_completo):
    return nome_completo.split(" ")[0]

def mensagem_nao_possui_conta(nome_completo):
    nome = retornar_primeiro_nome(nome_completo)
    print()
    console.print(f"[yellow]Sr(a) {nome}, você ainda não possui uma conta em nosso banco. Crie uma antes de realizar alguma movimentação.[/yellow]")

def mensagem_nao_cliente():
    print()
    console.print("[yellow]Você ainda não é cliente do Banco Python. Cadastre-se antes de criar uma conta.[/yellow]")

def mensagem_sem_transacoes(conta):
    print()
    console.print("[bold cyan]╠═════════════════════   EXTRATO   ═════════════════════╣[/bold cyan]")
    print()
    console.print(f" [green]Titular: {conta.cliente.nome}  -  Agência: {conta.agencia}  C/C: {conta.numero}[/green]")
    print()
    console.print("   [green]Você ainda não fez movimentações nessa conta.[/green]")
    print()
    console.print(f" [green]Saldo: R$ {conta.saldo:.2f}[/green]")
    print()
    console.print("[bold cyan]╠═══════════════════════════════════════════════════════╣[/bold cyan]")

def total_contas_criadas(clientes):
    return sum([len(cliente.contas) for cliente in clientes]) + 1



# FUNÇÕES PARA VERIFICAÇÃO BÁSICA
def procurar_cliente(clientes, cpf):
    clientes_encontrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_encontrados[0] if clientes_encontrados else None

def procurar_conta(cliente, numero):
    contas_encontradas = [conta for conta in cliente.contas if conta.numero == numero]
    return contas_encontradas[0] if contas_encontradas else None

def verificacao_padrao(clientes):
    cpf = str(Prompt.ask("\n[green]Insira seu CPF[/green]"))
    cliente_encontrado = procurar_cliente(clientes, cpf)
    possui_conta = cliente_encontrado.contas if cliente_encontrado else None

    if not cliente_encontrado:
        mensagem_nao_cliente()
        return

    elif not possui_conta:
        mensagem_nao_possui_conta(cliente_encontrado.nome)
        return

    else:
        return {"cliente": cliente_encontrado, "conta": possui_conta}



# FUNÇÃO PARA REALIZAÇÃO DO DEPÓSITO
@log_operacoes
def depositar(clientes):
    if not (cliente_e_contas := verificacao_padrao(clientes)):
        pass

    else:
        numero_conta = int(Prompt.ask("[green]Insira o número da conta onde será realizado o depósito[/green]"))
        conta = procurar_conta(cliente_e_contas["cliente"], numero_conta)

        if conta:
            valor = float(Prompt.ask("[green]Insira o valor a ser depositado[/green]"))
            deposito = Deposito(valor)
            cliente_e_contas["cliente"].realizar_transacao(conta, deposito)
        else:
            console.print("[red]Operação não realizada! Número de conta informado é inválido.[/red]")



# FUNÇÃO PARA REALIZAÇÃO DO SAQUE
@log_operacoes
def sacar(clientes):
    if not (cliente_e_contas := verificacao_padrao(clientes)):
        pass

    else:
        numero_conta = int(Prompt.ask("[green]Insira o número da conta onde será realizado o saque[/green]"))
        conta = procurar_conta(cliente_e_contas["cliente"], numero_conta)
        
        if conta:
            valor = float(Prompt.ask("[green]Insira o valor a ser sacado[/green]"))
            saque = Saque(valor)
            cliente_e_contas["cliente"].realizar_transacao(conta, saque)
        else:
            console.print("\n[red]Operação não realizada! Número de conta informado é inválido.[/red]")



# FUNÇÕES PARA EXIBIÇÃO DO EXTRATO
def menu_tipo_transacao():
    print()
    console.print("[bold cyan]╠═   Selecione a opção de transação   ═╣[/bold cyan]")
    print()
    console.print("[green][1] Depósitos[/green]")
    console.print("[green][2] Saques[/green]")
    console.print("[green][3] Todas[/green]")
    return int(input("\n-> ").strip())

def tipo_de_transacao_extrato():
    try:
        opcao = menu_tipo_transacao()
        match opcao:
            case 1:
                return "deposito"
            case 2:
                return "saque"
            case 3:
                return None
            case _:
                return ""
    
    except ValueError:
        console.print("\n[red]Entrada inválida. Por favor, digite um número.[/red]")

def exibir_extrato(conta, opcao):
    extrato = ""
    tem_transacao = False
    for transacao in conta.extrato.gerar_relatorio(tipo_transacao=opcao):
        tem_transacao = True
        tipo_transacao = "-" if transacao["tipo"] == "Saque" else "+"
        extrato += f"\n   [green]Tipo: {transacao["tipo"]}\n     {tipo_transacao}R$ {transacao["valor"]:.2f}         {transacao["data"]}[/green]"

    opcao = "saque" if opcao == 's' else "depósito"
    if not tem_transacao:
        extrato = f"\n   [green]Não foram feitas movimentações do tipo {opcao}[/green]"

    print()
    console.print("[bold cyan]╠═════════════════════   EXTRATO   ═════════════════════╣[/bold cyan]")
    print()
    console.print(f" [green]Titular: {conta.cliente.nome}  -  Agência: {conta.agencia}  C/C: {conta.numero}[/green]")
    console.print(extrato)
    print()
    console.print(f" [green]Saldo: R$ {conta.saldo:.2f}[/green]")
    print()
    console.print("[bold cyan]╠═══════════════════════════════════════════════════════╣[/bold cyan]")

def percorrer_contas_extrato(contas):
    opcao = tipo_de_transacao_extrato()
    for conta in contas:
        mensagem_sem_transacoes(conta) if not conta.extrato.transacoes else exibir_extrato(conta, opcao)

def menu_extrato():
    print()
    console.print("[bold cyan]╠═   Selecione a opção de extrato   ═╣[/bold cyan]")
    print()
    console.print("[green][1] Extrato de uma conta[/green]")
    console.print("[green][2] Extrato de todas as contas[/green]")
    return int(input("\n-> ").strip())

def extrato_uma_ou_todas(cliente):
    try:
        opcao = menu_extrato()
        match opcao:
            case 1:
                numero_conta = int(Prompt.ask("[green]Insira o número da conta[/green]"))
                conta = procurar_conta(cliente, numero_conta)

                if conta:
                    mensagem_sem_transacoes(conta) if not conta.extrato.transacoes else exibir_extrato(conta, tipo_de_transacao_extrato())

                else:
                    console.print("\n[red]Operação não realizada! Número de conta informado é inválido.[/red]")
            case 2:
                percorrer_contas_extrato(cliente.contas)            
            case _:
                console.print("[red]Selecione uma opção válida.[/red]")

    except ValueError:
        console.print("\n[red]Entrada inválida. Por favor, digite um número.[/red]")
@log_operacoes
def extrato(clientes):
    if not (cliente_e_contas := verificacao_padrao(clientes)):
        pass

    else:
        if len(cliente_e_contas["conta"]) > 1:
            extrato_uma_ou_todas(cliente_e_contas["cliente"])

        else:
            conta = cliente_e_contas["conta"][0]
            mensagem_sem_transacoes(conta) if not conta.extrato.transacoes else exibir_extrato(conta, tipo_de_transacao_extrato())


# FUNÇÕES PARA CADASTRO DO CLIENTE
def ler_dados_cliente():
    nome = str(Prompt.ask("[green]Digite o seu nome[/green]"))
    data_nascimento = str(Prompt.ask("[green]Digite sua data de nascimento (dd/mm/aa)[/green]"))
    endereco  = str(Prompt.ask("[green]Digite seu endereço (logradouro, número, distrito, cidade/SIGLA ESTADO)[/green]"))
    
    return {"nome": nome, "data_nascimento": data_nascimento, "endereco": endereco}
@log_operacoes
def cadastrar_cliente(clientes):
    cpf = str(Prompt.ask("\n[green]Insira seu CPF[/green]"))

    if not (cliente_encontrado := procurar_cliente(clientes, cpf)):
        dados_cliente = ler_dados_cliente()
        cliente = PessoaFisica(cpf=cpf,
                            nome=dados_cliente["nome"],
                            data_nascimento=dados_cliente["data_nascimento"],
                            endereco=dados_cliente["endereco"])
        clientes.append(cliente)
        console.print("\n[cyan]Cadastro realizado com sucesso! Você já pode usufurir dos benefícios do Banco Python.[/cyan]")
    
    else:
        nome = retornar_primeiro_nome(cliente_encontrado.nome)
        print()
        console.print(f"[cyan]\n Olá, {nome}. Você já é cliente do Banco Python, bem-vind@ de volta![/cyan]")



# FUNÇÕES PARA CRIAR CONTA CORRENTE
@log_operacoes
def criar_conta(clientes):
    cpf = str(Prompt.ask("\n[green]Insira seu CPF[/green]"))
    cliente_encontrado = procurar_cliente(clientes, cpf)

    if not cliente_encontrado:
        mensagem_nao_cliente()

    else:
        numero_de_contas = total_contas_criadas(clientes)
        conta_corrente = ContaCorrente.nova_conta(cliente=cliente_encontrado, numero=numero_de_contas)
        cliente_encontrado.adicionar_conta(conta_corrente)
        console.print(f"\n[cyan]Parabéns, sua conta foi criada com sucesso.\n{conta_corrente}[/cyan]")
        return {"cpf": cliente_encontrado.cpf, "numero": numero_de_contas}


@log_operacoes
def listar_contas(clientes):
    for cliente in clientes:
        for conta in ContaIterador(cliente.contas):
            print("\n ", "#" * 20)
            print(f"{conta}\n     Saldo: R$ {conta.saldo:.2f}")


clientes_banco_python = []

console = Console()
def menu_inicial():
    print()
    console.print("[bold cyan]╔══════════════════════╗[/bold cyan]")
    console.print("[bold cyan]     MENU PRINCIPAL[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════╝[/bold cyan]")
    print()
    console.print("[green][1] Depositar[/green]")
    console.print("[green][2] Sacar[/green]")
    console.print("[green][3] Extrato[/green]")
    console.print("[green][4] Cadastrar cliente[/green]")
    console.print("[green][5] Criar conta[/green]")
    console.print("[green][6] Listar contas[/green]")
    console.print("[red][7] Sair[/red]")
    return int(input("\n-> ").strip())

print()
console.print("[bold cyan]<-> BEM-VIND@ AO BANCO PYTHON <->[/bold cyan]")

def main():
    while True:

        try:
            opcao = menu_inicial()
            match opcao:
                case 1:
                    depositar(clientes_banco_python)
                case 2:
                    sacar(clientes_banco_python)
                case 3:
                    extrato(clientes_banco_python)
                case 4:
                    cadastrar_cliente(clientes_banco_python)
                case 5:
                    criar_conta(clientes_banco_python)
                case 6:
                    pass
                    listar_contas(clientes_banco_python)
                case 7:
                    console.print("\n[red]Saindo...[/red]")
                    break
                case _:
                    console.print("\n[red]Selecione uma opção válida.[/red]")

        except ValueError:
            console.print("\n[red]Entrada inválida. Por favor, digite um número.[/red]")

main()