#!/usr/bin/env python3  
import socket
import hashlib
import os

HOST = '0.0.0.0' #Escuta interna
PORT = 9999

BUFFER = 1024

#Create a Socket (connect two computers)
def create_socket():
    try:
        global socketUDP
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        return socketUDP
    
    except socket.error as msg:
        print("Socket creation error:" + str(msg))

#Binding the socket and listening for connections
def bind_socket(socketUDP):
    try:
        print("Binding the Port: "+ str(PORT))

        socketUDP.bind((HOST, PORT))

    except socket.error as msg:
        print("Socket Binding error" + str(msg) +"\n" + "Retrying...")
        bind_socket(socketUDP)

#Recebe comandos do cliente
def get_commands(data, adress):
    dataString = data.decode('utf-8')
    print(f'Endereco IP do cliente {adress} \n Mensagem:{dataString}')

    if dataString.startswith('GET'):
        fileName = dataString[4:]
        send_file(fileName, adress)

def checksumSHA256(data):
    #Inicializa um objeto hashlib com o algoritmo SHA-256
    hasher = hashlib.sha256()

    #Atualiza o hasher com os dados de entrada
    hasher.update(data)

    #Calcula o checksum SHA-256 e retorna em formato hexadecimal
    checksum = hasher.hexdigest()
    return checksum
    
#Envia arquivo solicitado pelo cliente
def send_file(fileName, adress):
    packge_num = 0

    if not os.path.isfile(fileName):
        print("Arquivo nao encontrado: " + fileName)
        socketUDP.sendto(b"1", adress)
    else:
        try:
            with open(fileName, 'rb') as f:
                while data := f.read(BUFFER): #Vai ler o arquivo com o tamanho especificado em Buffer
                    packge_num += 1

                    # Calcula checksum com SHA-256
                    checksum = checksumSHA256(data)

                    check = 'NOK'

                    #Verifica se o pacote foi enviado corretamente
                    while check == 'NOK':
                        socketUDP.sendto(checksum.encode('utf-8') + ";".encode('utf-8') + str(packge_num).encode('utf-8') + ">".encode('utf-8') + data, adress)
                        check = socketUDP.recvfrom(BUFFER)
                        check = check[0].decode('utf-8')
                        if check == 'NOK':
                            print('NOK recebido. Reenviando parte do arquivo.')
                    
        #Se o arquivo não existir
        except FileNotFoundError as msg:
            print("Deu algum error:" + str(msg + "\n"))
            socketUDP.sendto(b"ERRO!", adress)
            
        # Mensagem de finalização do arquivo
        print(f'Arquivo {fileName} enviado para {adress}')
        socketUDP.sendto(b'', adress)

def main():
    socketUDP = create_socket()
    bind_socket(socketUDP)

    print("Servidor está ouvindo em ", (HOST, PORT))

    enderecos = [] #Lista para armazenar enderecos dos clientes

    while True:
        data, adress = socketUDP.recvfrom(BUFFER)
        if(adress not in enderecos):
            enderecos.append(adress)
            get_commands(data, adress)
        print(f"Recebido de {adress}: {data.decode('utf-8')}")
    socketUDP.close()

main()