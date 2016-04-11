from Utility import *
from Communication import *
from Parser import *
import asyncore
import logging
import os

class ReceiveHandler(asyncore.dispatcher):

    def __init__(self, conn_sock, address):
        asyncore.dispatcher.__init__(self,conn_sock)
        self.conn_sock = conn_sock
        self.address = address
        self.out_buffer = []

##  metodo di scrittura sul buffer, quando pronto viene svuotato
##  molto utile per l'upload
    def write(self, data):
        self.out_buffer.append(data)

##  eventuale metodo per chiudere la connessione
##  questo va utilizzato se si vuole evitare di ricevere 0
    def shutdown(self):
        self.out_buffer.append(None)

##  overide metodo handle_read
    def handle_read(self):

        data = self.recv(2048)
        logging.debug(data)

        if len(data) > 0:
            # converto i comandi
            command, fields = Parser.parse(data.decode())

            if command == "RETR":
                # Imposto la lunghezza dei chunk e ottengo il nome del file a cui corrisponde l'md5
                chuncklen = 512
                peer_md5 = fields[0]
                obj = Utility.database.findFile(peer_md5)

                if len(obj) > 0:
                    # svuota il buffer
                    self.out_buffer = []
                    filename = Utility.PATHDIR + str(obj[0][0])
                    # lettura statistiche file
                    statinfo = os.stat(filename)
                    # imposto lunghezza del file
                    len_file = statinfo.st_size
                    # controllo quante parti va diviso il file
                    num_chunk = len_file // chuncklen
                    if len_file % chuncklen != 0:
                        num_chunk = num_chunk + 1
                    # pad con 0 davanti
                    num_chunk = str(num_chunk).zfill(6)
                    # costruzione risposta come ARET0000XX
                    mess = ('ARET' + num_chunk).encode()
                    self.write(mess)

                    # Apro il file in lettura e ne leggo una parte
                    f = open(filename, 'rb')
                    r = f.read(chuncklen)

                    # Finchè il file non termina
                    while len(r) > 0:

                        # Invio la lunghezza del chunk
                        mess = str(len(r)).zfill(5).encode()
                        self.write(mess + r)
                        logging.debug('messaggio nel buffer pronto')

                        # Proseguo la lettura del file
                        r = f.read(chuncklen)
                    # Chiudo il file
                    f.close()
                    self.shutdown()

            elif(command == "QUER"):
                msgRet = 'AQUE'
                # Prendo i campi del messaggio ricevuto
                pkID = fields[0]
                ipDest = fields[1]
                portDest = fields[2]
                ttl = fields[3]
                name = fields[4]

                # Controllo se il packetId è già presente se è presente non rispondo alla richiesta
                # E non la rispedisco
                if Utility.database.checkPkt(pkID)==False:
                    Utility.database.addPkt(pkID)
                    # Esegue la risposta ad una query
                    msgRet = msgRet + pkID
                    ip = Utility.MY_IPV4 + '|' + Utility.MY_IPV6
                    port = '{:0>5}'.format(Utility.PORT)
                    msgRet = msgRet + ip + port
                    l = Utility.database.findMd5(name.strip(' '))

                ##  manda la risposta di AQUE per tutti i risultati trovati
                    for i in range(0, len(l)):
                        f = Utility.database.findFile(l[i][0])
                        r = msgRet
                        r = r + l[i][0] + str(f[0][0]).ljust(100, ' ')
                        t1 = Sender(r, ipDest, portDest)
                        t1.start()

                    # controllo se devo divulgare la query
                    if int(ttl) >= 1:
                        ttl='{:0>2}'.format(int(ttl)-1)
                        msg="QUER"+pkID+ipDest+portDest+ttl+name
                        lista= Utility.database.listClient()
                        if len(lista)>0:
                            t2 = SenderAll(msg, lista)
                            t2.run()

            elif command=="AQUE":
                pkID = fields[0]
                if Utility.database.checkPkt(pkID)==True and fields[3] not in Utility.listFindFile:
                    Utility.numFindFile+=1
                    ipServer = fields[1]
                    portServer = fields[2]
                    md5file = fields[3]
                    filename = str(fields[4]).strip()
                    Utility.listFindFile.append(fields)
                    print(str(Utility.numFindFile) + " " + ipServer + " " + md5file + " " + filename)

            elif command=="NEAR":
                if Utility.database.checkPkt(fields[0])==False:

                    pkID = fields[0]
                    ipDest = fields[1]
                    portDest = fields[2]
                    ttl = int(fields[3])

                    Utility.database.addPkt(pkID)
                    ip=Utility.MY_IPV4+"|"+Utility.MY_IPV6
                    port='{:0>5}'.format(Utility.PORT)
                    msgRet="ANEA"+pkID+ip+port
                    t=Sender(msgRet,ipDest,portDest)
                    t.start()
                    ttl = ttl-1
                    if ttl > 0:
                        ttl='{:0>2}'.format(ttl)
                        msg="NEAR"+pkID+ipDest+portDest+ttl
                        lista=Utility.database.listClient()
                        if len(lista)>0:
                            t1 = SenderAll(msg,lista )
                            t1.run()

            elif command=="ANEA":
                lista=Utility.database.listClient()
                find=False
                pkID=fields[0]
                ip=fields[1]
                port=fields[2]
                for i in range(0,len(lista)):
                    if lista[i][0]==ip and lista[i][1]==port:
                        find=True
                if Utility.database.checkPkt(pkID)==True and find==False:
                    Utility.database.addClient(ip,port)

            else:
                logging.debug('ricevuto altro')

##   metodo che verifica la possibilita' di scrivere delle
##   informazioni sul canale
    def writable(self):
        return (len(self.out_buffer) > 0)

##  metodo per scrivere in uscita dal canale
    def handle_write(self):
        if self.out_buffer[0] is None:
            logging.debug('informazione trasferita')
            self.close()
            return

        sent = self.send(self.out_buffer[0])
        logging.debug('sto svuotando il buffer')
        # sistemare eventuale errore NoneType su out_buffer
        if sent >= len(self.out_buffer[0]):
            self.out_buffer.pop(0)
        else:
            self.out_buffer[0] = self.out_buffer[0][sent:]

##  metodo per chiudere il canale
    def handle_close(self):
        logging.debug('sto uscendo dal canale')
        self.close()

