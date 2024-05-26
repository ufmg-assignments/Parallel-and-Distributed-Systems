import grpc
from sys import stdin, argv
import integracao_pb2
import integracao_pb2_grpc
import diretorio_pb2
import diretorio_pb2_grpc

def cliente_integrado():

    # Obtem o endereco, cria um canal e um stub
    endereco = argv[1]
    canal = grpc.insecure_channel(endereco)
    stub = integracao_pb2_grpc.ServidorIntegracaoStub(canal)

    # Loop para ler os comandos da entrada padrão
    for comando in stdin:
    
        # Faz o processamento do comando e obtem seu tipo
        comando = comando.replace("\n", "")
        comando = comando.split(",")
        tipo = comando[0]
        
        # Se o tipo for de Consulta, envia-se uma chave para ser consultada no servidor de integracao
        if tipo == "C":
            ch = comando[1]
            resposta = stub.consultar_servidor(integracao_pb2.ConsultaIntegracaoRequest(chave=int(ch)))
            
            # Se a chave nao for encontrada no servidor de integracao, printa-se "ND"
            if resposta.nome_maquina == "ND":
                print("ND")
                
            # Caso contrario, busca se a descricao e o valor associados a chave no
            # servidor de diretorios retornado na resposta
            else:
                endereco_diretorio = f"{resposta.nome_maquina}:{resposta.porto}"
                canal_diretorio = grpc.insecure_channel(endereco_diretorio)
                stub_diretorio = diretorio_pb2_grpc.ServidorDiretorioStub(canal_diretorio)
                resposta_diretorio = stub_diretorio.consultar_diretorio(diretorio_pb2.ConsultaRequest(chave=int(ch)))
                
                if resposta_diretorio.desc == "":
                    print(-1)
                else:
                    print(f"{resposta_diretorio.desc},{resposta_diretorio.valor:7.4f}")
            
        # Se o tipo for de Termino, termina a execucao do servidor e imprime o numero total
        # de chaves guardadas no servidor de integracao
        elif tipo == "T":
            resposta = stub.terminar_servidor_integrado(integracao_pb2.TerminoIntegracaoRequest())
            print(resposta.num_chaves)
            break
            
        # Se o tipo nao for reconhecido, continua para o próximo comando
        else:
            continue

# Chama a funcao cliente_integrado quando o script for executado
if __name__ == "__main__":
    cliente_integrado()
