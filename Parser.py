import re

# Classe che implementa i metodi per eseguire controlli e suddivisioni del messaggio ricevuto
class Parser:

    # Metodo statico che si occupa di suddividere i vari campi di data in modo consono
    @staticmethod
    def parse(data):

        # Inizializzo il contenitore dei vari campi
        fields = {}

        # Prendo i primi 4 caratteri maiuscoli all'interno di data e li inserisco in command
        command = data[0:4]

        # Se il comando è QUER suddivido data in questo modo
        if command == 'QUER':
            fields[0] = data[4:20]    # PKTID[16B]
            fields[1] = data[20:75]   # IPP2P[55B]
            fields[2] = data[75:80]   # PP2P[5B]
            fields[3] = data[80:82]   # TTL[2B]
            fields[4] = data[-20:]    # Ricerca[20B]

        # Se il comando è AQUE suddivido data in questo modo
        elif command == 'AQUE':
            fields[0] = data[4:20]    # PKTID[16B]
            fields[1] = data[20:75]   # IPP2P[55B]
            fields[2] = data[75:80]   # PP2P[5B]
            fields[3] = data[80:112]  # FileMD5[32B]
            fields[4] = data[-100:]   # FileName[100B]

        # Se il comando è NEAR suddivido data in questo modo
        elif command == 'NEAR':
            fields[0] = data[4:20]    # PKTID[16B]
            fields[1] = data[20:75]   # IPP2P[55B]
            fields[2] = data[75:80]   # PP2P[5B]
            fields[3] = data[-2:]     # TTL[2B]

            # Se il comando è ANEA suddivido data in questo modo
        elif command == 'ANEA':
            fields[0] = data[4:20]    # PKTID[16B]
            fields[1] = data[20:75]   # IPP2P_j[55B]
            fields[2] = data[-5:]     # PP2P_j[5B]

        # Se il comando è RETR suddivido data in questo modo
        elif command == 'RETR':
            fields[0] = data[-32:]    # FileMD5[32B]

        # Se il comando è ARET suddivido data in questo modo
        elif command == 'ARET':
            fields[0] = data[4:10]    # nChunk[6B]

        # Se questo else viene eseguito significa che il comando ricevuto non è previsto
        else:
            print('Errore durante il parsing del messaggio\n')

        # Eseguo il return del comando e dei campi del messaggio
        return command, fields



    # Metodo statico che controlla la corretta formattazione del parametro data
    @staticmethod
    def check(data):

        # Inizializzo la lista di comandi e un flag degli errori
        command_list = ['QUER', 'AQUE', 'NEAR', 'ANEA', 'RETR', 'ARET']
        error = False

        # Controllo che il comando sia effettivamente tra quelli riconosciuti
        command = data[0:4]
        if command not in command_list:
            error = True
            print('Errore, comando (' + command + ') non riconosciuto \n')

        # Se il comando è QUER eseguo questi controlli tramite regex
        if command == 'QUER' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}\d{2}[\da-zA-Z\.\ ]{20}$')
            if p.search(data) == None:
                error = True

        # Se il comando è AQUE eseguo questi controlli tramite regex
        elif command == 'AQUE' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}[\da-zA-Z]{32}[\da-zA-Z\.\ ]{100}$')
            if p.search(data) == None:
                error = True

        # Se il comando è NEAR eseguo questi controlli tramite regex
        elif command == 'NEAR' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}\d{2}$')
            if p.search(data) == None:
                error = True

        # Se il comando è ANEA eseguo questi controlli tramite regex
        elif command == 'ANEA' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}$')
            if p.search(data) == None:
                error = True

        # Se il comando è RETR eseguo questi controlli tramite regex
        elif command == 'RETR' and not error:
            p = re.compile('[\da-zA-Z]{32}$')
            if p.search(data) == None:
                error = True

        # Se il comando è ARET suddivido data in questo modo
        elif command == 'ARET' and not error:
            p = re.compile('\d{6}')
            if p.search(data) == None:
                error = True

        # Se questo else viene eseguito significa che il comando ricevuto non è previsto
        if not error:
            print('Il messaggio è ben formattato\n')
        else:
            print('Errore' + data + '\n')