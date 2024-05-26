import grpc
import threading
from concurrent import futures
from sys import argv
import integracao_pb2
import integracao_pb2_grpc

# Classe que implementa os procedimentos do servidor de integracao
class ServidorIntegracao(integracao_pb2_grpc.ServidorIntegracaoServicer):

    def __init__(self, stop_event_int):
    
        # Dicionario para armazenar os servidores ja integrados e suas chaves
        self.servidores_integrados = {}
        self._stop_event_int = stop_event_int

    def registrar_servidor(self, request, context):
    
        # Variaveis para guardar os parametros passados
        nome_maquina = request.nome_maquina
        porto = request.porto
        chaves = eval(request.chaves)

        # Tenta-se adicionar o servidor ao dicionario de servidores integrados e
        # responde com o tamanho da lista de chaves passado
        try:
            self.servidores_integrados[(nome_maquina, porto)] = chaves
            return integracao_pb2.RespostaRegistroIntegracao(num_chaves=len(chaves))
           
        # Caso algum erro seja detectado, retorna-se 0 como resposta
        except:
            return integracao_pb2.RespostaRegistroIntegracao(num_chaves=0)

    def consultar_servidor(self, request, context):
        chave = request.chave

        # Verifica em todos os servidores integrados se a chave existe
        for identificacao, chaves in self.servidores_integrados.items():
        
            # Se algum servidor tiver a chave, retorna-se o nome da maquina e o porto associados
            if chave in chaves:
                return integracao_pb2.RespostaConsultaIntegracao(nome_maquina=identificacao[0], porto=identificacao[1])
        
        # Caso nao haja a chave, retorna-se "ND"
        return integracao_pb2.RespostaConsultaIntegracao(nome_maquina="ND", porto=0)  # Retorna "ND" e 0 se a chave nao for encontrada

    def terminar_servidor_integrado(self, request, context):
    
        # Primeiro, conta-se o total de chaves guardadas no servidor de integracao
        total_chaves = 0
        for chaves in self.servidores_integrados.values():
            total_chaves += len(chaves)

        # Indica que o servidor deve terminar a execucao
        self._stop_event_int.set()
        
        # Retorna-se como resposta o total de chaves 
        return integracao_pb2.RespostaTerminoIntegracao(num_chaves=total_chaves)


def servidor_integrado():

    # Cria um evento para sinalizar a parada do servidor de integracao
    stop_event_int = threading.Event()
    
    # Cria-se o servidor gRPC e adiciona a implementacao do servico ServidorIntegracao a instancia
    server_int = grpc.server(futures.ThreadPoolExecutor())
    integracao_pb2_grpc.add_ServidorIntegracaoServicer_to_server(ServidorIntegracao(stop_event_int), server_int)
    
    # Obtem a porta passada como parametro e cria-se o endereco
    porta = argv[1]
    endereco = f"[::]:{porta}"
    
    # Adiciona-se o endereco ao servidor e o executa ate a sinalizacao do evento de parada
    server_int.add_insecure_port(endereco)
    server_int.start()
    stop_event_int.wait()
    server_int.stop(0)

# Chama a funcao servidor_integrado quando o script for executado
if __name__ == "__main__":
    servidor_integrado()
