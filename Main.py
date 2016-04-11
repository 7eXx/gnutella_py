from Communication import *
from Server import *
from Utility import *
import os

# TODO completare con la lista dei near iniziali
# database.addClient(ip="172.030.007.001|fc00:0000:0000:000:0000:0000:0007:0001",port="3000")
Utility.database.addClient(ip="172.030.007.010|fc00:0000:0000:0000:0000:0000:0007:0010",port="3000")

# logging.basicConfig(level=logging.DEBUG)

ipv4, ipv6 = Utility.getIp(Utility.MY_IPV4 +"|" + Utility.MY_IPV6)
Server_Peer(ipv4, ipv6)



while True:
    print("1. Ricerca")
    print("2. Aggiorna Vicini")
    print("3. Aggiungi File")
    print("4. Rimuovi File")
    print("5. Visualizza File")
    print("6. Visualizza Vicini")
    print("7. Aggiungi Vicino")
    print(" ")
    sel=input("Inserisci il numero del comando da eseguire ")
    if sel=="1":
        sel=input("Inserisci stringa da ricercare ")
        while len(sel)>20:
            sel=input("Stringa Troppo Lunga,reinserisci ")
        pktID=Utility.generateId(16)
        ip=Utility.MY_IPV4+'|'+Utility.MY_IPV6
        port='{:0>5}'.format(Utility.PORT)
        ttl='{:0>2}'.format(5)
        search=sel.ljust(20,' ')
        msg="QUER"+pktID+ip+port+ttl+search
        Utility.database.addPkt(pktID)
        Utility.numFindFile = 0
        Utility.listFindFile = []
        lista=Utility.database.listClient()
        if len(lista)>0:
            t1 = SenderAll(msg, lista)
            t1.run()

        # Visualizzo le possibili scelte
        print("Scelta  PEER                                                        MD5                       Nome")

        # Chiedo quale file scaricare
        i = -1
        while i not in range(0, Utility.numFindFile +1):
            i = int(input("Scegli il file da scaricare oppure no (0 Non scarica nulla)\n"))
            if Utility.database.checkPkt(pktID) == False:
                break

        if Utility.numFindFile == 0:
            print ("Nessun risultato di ricerca ricevuto")

        elif i > 0:
            i = i - 1;
            ipp2p = Utility.listFindFile[i][1]
            pp2p = Utility.listFindFile[i][2]
            md5file = Utility.listFindFile[i][3]
            filename = str(Utility.listFindFile[i][4]).strip()

            try:
                # thread falso per avviare in simultanea si usa start
                t1 = Downloader(ipp2p, pp2p, md5file, filename)
                t1.run()
            except Exception as e:
                print(e)

    elif sel=="2":
        listaNear=Utility.database.listClient()
        if len(listaNear)>0:
            pktID=Utility.generateId(16)
            ip=Utility.MY_IPV4+'|'+Utility.MY_IPV6
            port='{:0>5}'.format(Utility.PORT)
            ttl='{:0>2}'.format(2)
            msg="NEAR"+pktID+ip+port+ttl
            Utility.database.addPkt(pktID)
            Utility.database.removeAllClient()
            t1 = SenderAll(msg, listaNear)
            t1.run()

    elif sel=="3":

        # Rimuovo i file presenti al momento nel database
        Utility.database.removeAllFile()

        #Ottengo la lista dei file dalla cartella corrente
        lst = os.listdir(Utility.PATHDIR)

        #Inserisco i file nel database
        if len(lst) > 0:
            for file in lst:
                Utility.database.addFile(Utility.generateMd5(Utility.PATHDIR+file), file)
            print("Operazione completata")
        else:
            print("Non ci sono file nella directory")

    elif sel=="4":

        # Ottengo la lista dei file dal database
        lst = Utility.database.listFile()

        # Visualizzo la lista dei file
        if len(lst) > 0:
            print("Scelta  MD5                                        Nome")
            for i in range(0,len(lst)):
                print(str(i) + "   " + lst[i][0] + " " + lst[i][1])

            # Chiedo quale file rimuovere
            i = -1
            while i not in range(0, len(lst)):
                i = int(input("Scegli il file da cancellare "))

            # Elimino il file
                Utility.database.removeFile(lst[i][0])
            print("Operazione completata")
        else:
            print("Non ci sono file nel database")

    elif sel=="5":

        # Ottengo la lista dei file dal database
        lst = Utility.database.listFile()

        # Visualizzo la lista dei file
        if len(lst) > 0:
            print("MD5                                        Nome")
            for file in lst:
                print(file[0] + " " + file[1])
        else:
            print("Non ci sono file nel database")

    elif sel=="6":
        lista= Utility.database.listClient()
        print(" ")
        print("IP e PORTA")
        for i in range(0,len(lista)):
            print("IP"+str(i)+" "+lista[i][0]+" "+lista[i][1])

    elif sel=="7":
        sel=input("Inserici Ipv4 [tipo 0.0.0.0]")
        t=sel.split('.')
        ipv4=""
        ipv4=ipv4+'{:0>3}'.format(t[0])+'.'
        ipv4=ipv4+'{:0>3}'.format(t[1])+'.'
        ipv4=ipv4+'{:0>3}'.format(t[2])+'.'
        ipv4=ipv4+'{:0>3}'.format(t[3])+'|'
        sel=input("Inserici Ipv6 [tipo 0:0:0:0:0:0:0:0")
        t=sel.split(':')
        ipv6=""
        ipv6=ipv6+'{:0>4}'.format(t[0])+':'
        ipv6=ipv6+'{:0>4}'.format(t[1])+':'
        ipv6=ipv6+'{:0>4}'.format(t[2])+':'
        ipv6=ipv6+'{:0>4}'.format(t[3])+':'
        ipv6=ipv6+'{:0>4}'.format(t[4])+':'
        ipv6=ipv6+'{:0>4}'.format(t[5])+':'
        ipv6=ipv6+'{:0>4}'.format(t[6])+':'
        ipv6=ipv6+'{:0>4}'.format(t[7])
        sel=input("Inserici Porta ")
        port='{:0>5}'.format(int(sel))
        ip=ipv4+ipv6
        Utility.database.addClient(ip,port)
    else:
        print("Commando Errato, attesa nuovo comando ")

