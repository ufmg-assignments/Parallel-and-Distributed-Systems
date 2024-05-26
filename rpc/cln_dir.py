import grpc
from sys import stdin, argv
import diretorio_pb2
import diretorio_pb2_grpc

def cliente():

    # Obtem o endereco, cria um canal e um stub
    endereco = argv[1]
    canal = grpc.insecure_channel(endereco)
    stub = diretorio_pb2_grpc.ServidorDiretorioStub(canal)

    # Loop para ler os comandos da entrada padrão
    for comando in stdin:
    
        # Faz o processamento do comando e obtem seu tipo
        comando = comando.replace("\n", "")
        comando = comando.split(",")    
        tipo = comando[0]

	# Se o tipo for de Insercao, insere a descricao e o valor na chave do diretorio
        if tipo == "I":
            ch, desc, val = comando[1], comando[2], comando[3]
            resposta = stub.inserir_no_diretorio(diretorio_pb2.InsercaoRequest(chave=int(ch), descricao=desc, valor=float(val)))
            print(resposta.inseriu)
            
        # Se o tipo for de Consulta, busca-se a descricao e o valor da chave passada no diretorio
        elif tipo == "C":
            ch = int(comando[1])
            resposta = stub.consultar_diretorio(diretorio_pb2.ConsultaRequest(chave=ch))
            
            # Se nao houver a chave no diretorio, printa -1
            if resposta.existe == "false":
                print(-1)
            else:
                print(f"{resposta.desc},{resposta.valor:7.4f}")
                
        # Se o tipo for de Registro, envia o comando para o servidor de diretorio associado, que deve se
        # registrar no servidor de integracao informado. Ao final, printa-se o numero de chaves do servidor registrado
        elif tipo == "R":
            nome_int, porto_int = comando[1], int(comando[2])
            resposta = stub.registrar_no_servidor(diretorio_pb2.RegistroRequest(nome_srv_int=nome_int, porto_srv_int=porto_int))
            print(resposta.num_chaves)
            
        # Se o tipo for de Termino, termina a execucao do servidor e imprime o numero de chaves guardados
        elif tipo == "T":
            resposta = stub.terminar_execucao(diretorio_pb2.TerminoRequest())
            print(resposta.num_chaves)
            break
            
        # Se o tipo nao for reconhecido, continua para o proximo comando
        else:
            continue

# Chama a funcao cliente quando o script for executado
if __name__ == "__main__":
    cliente()
