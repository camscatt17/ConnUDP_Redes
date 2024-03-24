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
    recvFile = 'recvFile.txt'
    backupFile = 'bckFile.txt'

    try:
        # Envia a mensagem de solicitação para o servidor
        socketUDP.sendto(f"GET {filename}".encode(), server_address)
        
        # Recebe os dados do servidor em blocos e os imprime
        with open(recvFile, 'wb') as recv_file, open (backupFile, 'wb') as bck_file:   
            while True:
                data, _ = socketUDP.recvfrom(BUFFER)
                if not data:
                    break  # Se não há mais dados, sai do loop
                
                bck_file.write(data)
                
                #Opção para o usuário descartar uma parte do arquivo (Simular perda de pacotes)
                discard = input("Deseja descartar uma parte do arquivo? (s/n): ")
                if discard.lower() == 's':
                    percent_to_discard = float(input("Informe a porcentagem do arquivo a ser descartada (0-100): "))
                    bytes_to_discard = int(len(data) * (percent_to_discard / 100))
                    data_discarded = data[:bytes_to_discard]
                    data = data[bytes_to_discard:]
                    recv_file.write(data_discarded)

                # Verifica o checksum e solicita reenvio em caso de falha
                if not confere_checksum(data):
                    print("Erro de checksum. Requisitando reenvio.")
                    continue
            
            print(f'Dados originais escritos no arquivo {recvFile}')
            print(f'Dados descartados escritos no arquivo de backup {backupFile}')
    
    except Exception as e:
        print(f"Ocorreu um erro durante a comunicação com o servidor: {e}")
    
    finally:
        # Fecha o socket do cliente
        print("Finalizado. Fechando conexão com o servidor.")
        socketUDP.close()

if __name__ == "__main__":
    main()