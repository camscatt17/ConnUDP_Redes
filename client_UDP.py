#!/usr/bin/env python3  
import socket
import hashlib

SERVER_IP = 'localhost'
SERVER_PORT = 9999
BUFFER = 1024

def create_socket():
    try:
        global client_socketUDP
        client_socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        return client_socketUDP
    
    except socket.error as msg:
        print("Socket creation error:" + str(msg))  

def confere_checksum(dados):
    #Resgata checksum do servidor
    checksum_recebido = dados[:32] #SHA-256 gera um digest de 32 bytes
    
    #Calcula novo checksum
    novos_dados = dados[32:]
    novo_checksum = hashlib.sha256(novos_dados).digest()

    #retorna True se os checksum forem iguais e False, caso contrário
    return checksum_recebido == novo_checksum

def main():
    # Inicializa o socket UDP
    socketUDP = create_socket()
    server_address = (SERVER_IP, SERVER_PORT)

    filename = "lorem.txt"
    newFile = 'recvFile.txt'

    try:
        # Envia a mensagem de solicitação para o servidor
        socketUDP.sendto(f"GET {filename}".encode(), server_address)
        
        # Recebe os dados do servidor em blocos e os imprime
        with open(newFile, 'wb') as file_recv:   
            while True:
                data, _ = socketUDP.recvfrom(BUFFER)
                if not data:
                    break  # Se não há mais dados, sai do loop
                file_recv.write(data)
            print(f'Dados escritos no arquivo {newFile}')
        
    except Exception as e:
        print(f"Ocorreu um erro durante a comunicação com o servidor: {e}")
    
    finally:
        # Fecha o socket do cliente
        print("Finalizado. Fechando conexão com o servidor.")
        socketUDP.close()

if __name__ == "__main__":
    main()