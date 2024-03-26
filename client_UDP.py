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

def confere_checksum(dados, hash_received):
    hash_received = hash_received.decode('utf-8')
    print("hash_received")
    print(hash_received)

    #Inicializa um objeto hashlib com o algoritmo SHA-256
    hasher = hashlib.sha256()

    #Atualiza o hasher com os dados de entrada
    hasher.update(dados)

    #Calcula o checksum SHA-256 e retorna em formato hexadecimal
    novo_checksum = hasher.hexdigest()
    print("Novo CHeck sum")
    print(novo_checksum)

    #retorna True se os checksum forem iguais e False, caso contrário
    flag = hash_received == novo_checksum
    print(flag)
    return flag
    

def main():
    # Inicializa o socket UDP
    socketUDP = create_socket()
    server_address = (SERVER_IP, SERVER_PORT)

    recvFile = 'recvFile.txt'
    backupFile = 'bckFile.txt'
    package_count = 0

    arquivo = input('Insira o nome do arquivo + extensão \".txt\"\n')
    bytesEnviados = str.encode('GET ' + arquivo)

    # Envia a mensagem de solicitação para o servidor
    client_socketUDP.sendto(bytesEnviados, server_address)

    try:
        flag_error = 1
        
        # Recebe os dados do servidor em blocos e os imprime
        with open(recvFile, 'wb') as recv_file, open (backupFile, 'wb') as bck_file:
            while True:
                data, _ = socketUDP.recvfrom(BUFFER)
                if data.decode("utf-8") == "1":
                    print('Arquivo nao encontrado')
                    flag_error = 0
                    break
                elif data.startswith('ERRO!'.encode('utf-8')):
                    print(data.decode('utf-8'))
                    flag_error = 0
                    break
                elif not data:
                    print('Arquivo finalizado!')
                    break  # Se não há mais dados, sai do loop
                
                bck_file.write(data)
                hash_received, _ = socketUDP.recvfrom(BUFFER)
                
                package_count += 1

                #Opção para o usuário descartar uma parte do arquivo (Simular perda de pacotes)
                discard = input("Deseja descartar uma parte do arquivo? (s/n): ")
                if discard.lower() == 's':
                    percent_to_discard = float(input("Informe a porcentagem do arquivo a ser descartada (0-100): "))

                    bytes_to_discard = int(len(data) * ((100 - percent_to_discard) / 100))
                    data_dicard = data[:bytes_to_discard]
                    data = data_dicard

                # Verifica o checksum e solicita reenvio em caso de falha
                if confere_checksum(data, hash_received):
                    recv_file.write(data)
                    print(f'Pacote {package_count} enviado!')
                    check = 'OK'.encode('utf-8')
                else:
                    print(f'Erro de checksum no pacote {package_count}. Uma parte do arquivo foi perdida.\nRequisitando reenvio.')
                    check = 'NOK'.encode('utf-8')
    
                socketUDP.sendto(check, server_address)
            if flag_error:
                print(f'Todos os dados recebidos do servidor escritos em: {backupFile}')
                print(f'Somente os dados validos (excluido os dados que vieram faltando) {recvFile}')
    
    except Exception as e:
        print(f"Ocorreu um erro durante a comunicação com o servidor: {e}")
    
    finally:
        # Fecha o socket do cliente
        print("Finalizado. Fechando conexão com o servidor.")
        socketUDP.close()

if __name__ == "__main__":
    main()