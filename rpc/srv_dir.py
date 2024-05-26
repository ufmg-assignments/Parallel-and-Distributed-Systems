import grpc
import threading
from concurrent import futures
from sys import argv
import socket
import diretorio_pb2
import diretorio_pb2_grpc
import integracao_pb2
import integracao_pb2_grpc

# Classe que implementa os procedimentos do servidor de diretorios
class ServidorDiretorio(diretorio_pb2_grpc.ServidorDiretorioServicer):

    def __init__(self, stop_event):
    
        # Dicionario para armazenar as chaves e suas respectivas descricoes e valores
        self.diretorio = {}
        self._stop_event = stop_event

    def inserir_no_diretorio(self, request, context):
    
        # Variaveis para guardar os parametros passados
        chave = request.chave
        desc = request.descricao
        valor = request.valor

        # Se a chave ja existir no diretorio, a descricao e o valor sao atualizados
        if chave in self.diretorio:
            self.diretorio[chave] = (desc,valor)
            return diretorio_pb2.RespostaInsercao(inseriu=1)
            
        # Caso contrario, insere a nova chave, descricao e valor no diretorio
        else:
            self.diretorio[chave] = (desc,valor)
            return diretorio_pb2.RespostaInsercao(inseriu=0)

    def consultar_diretorio(self, request, context):
        chave = request.chave

        # Se a chave existir no diretorio, a descricao e o valor associados sao retornados
        if chave in self.diretorio:
            descricao, val = self.diretorio[chave]
            return diretorio_pb2.RespostaConsulta(desc=descricao, valor=val, existe="true")
            
        # Caso contrario, retorna-se que a chave nao existe no diretorio
        else:
            return diretorio_pb2.RespostaConsulta(desc="", valor=0, existe="false")

    def registrar_no_servidor(self, request, context):
    
        # Variaveis para guardar o nome da maquina do servidor de diretorios atual, o nome da 
        # maquina do servidor de integracao e o seu porto
        nome_maquina = socket.getfqdn()
        nome_int = request.nome_srv_int
        porto_int = request.porto_srv_int

        # Constroi o endereco, cria um canal e um stub
        endereco_integracao = f"{nome_int}:{porto_int}"
        canal_integracao = grpc.insecure_channel(endereco_integracao)
        stub_integracao = integracao_pb2_grpc.ServidorIntegracaoStub(canal_integracao)
        
        # Registra o servidor de diretorios atual no servidor de integracao
        resposta = stub_integracao.registrar_servidor(integracao_pb2.RegistroIntegracaoRequest(nome_maquina=nome_maquina, porto=int(argv[1]),chaves=str(list(self.diretorio.keys()))))

        # Retorna-se o numero de chaves da resposta do servidor de integracao
        return diretorio_pb2.RespostaIntegracao(num_chaves=resposta.num_chaves)

    def terminar_execucao(self, request, context):
        total_chaves = len(self.diretorio)
        
        # Indica que o servidor deve terminar a execucao
        self._stop_event.set()
        
        # Retorna-se como resposta o numero de chaves guaradados no diretorio 
        return diretorio_pb2.RespostaTermino(num_chaves=total_chaves)

def servidor():

    # Cria um evento para sinalizar a parada do servidor de diretorios
    stop_event = threading.Event()
    
    # Cria-se o servidor gRPC e adiciona a implementacao do servico ServidorDiretorio a instancia
    server = grpc.server(futures.ThreadPoolExecutor())
    diretorio_pb2_grpc.add_ServidorDiretorioServicer_to_server(ServidorDiretorio(stop_event), server)

    # Obtem a porta passada como parametro e cria-se o endereco
    porta = argv[1]
    endereco = f"[::]:{porta}"

    # Adiciona-se o endereco ao servidor e o executa ate a sinalizacao do evento de parada
    server.add_insecure_port(endereco)
    server.start()
    stop_event.wait()
    server.stop(0)
    
# Chama a funcao servidor quando o script for executado
if __name__ == "__main__":
    servidor()
