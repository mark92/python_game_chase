#!/usr/bin/env python
from curses import flash,beep,noecho,initscr,curs_set,newwin,endwin,KEY_RIGHT,KEY_LEFT,KEY_DOWN,KEY_UP
import time
import random
import socket
import math
import os
import urllib2

#Pasirinkimas prisijungti arba paleisti serveri
option = raw_input("[1] Host\n[2] Connect\n[3] Reconnect\n[4] Local\n")

#Vienetas(1) reiskia serveris, dvejetas(2) reiskia klientas, trejetas(3) reiskia persijungima ir bus pakeistas 2, jei keturi(4) ijungiamas lokalus rezimas
if option == '1':
    ipFinder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ipFinder.connect(("google.com", 80))
    host = ipFinder.getsockname()[0]  # IP
    servPort = 12345
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    extHost = urllib2.urlopen('http://ip.42.pl/raw').read()

    print 'Server started! Local IP: ' + host + "  External IP: " + extHost
    print 'Waiting for clients...'

    serverSock.bind((host, servPort))
    serverSock.listen(5)
    clientSock, addr = serverSock.accept()
    print 'Got connection from', addr

elif option == '2' or option == '3':
    serverSock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    if option == '3':
        try:
            file = open(os.path.abspath(__file__).replace('chase.py','',1) + 'chaseLast','r')
            host = file.readline()
            file.close()
            option = '2'
        except IOError:
            print "There is no last connection"
            exit()
    else:
        host = raw_input('Enter IP of the host: ')
    file = open(os.path.abspath(__file__).replace('chase.py','',1) + 'chaseLast','w')
    file.write(host)
    file.close()
    port = 12345

    print 'Connecting to: ', host, port
    serverSock.connect((host, port))

elif option != '4': print("\nBad input! bb"); exit()

#Serveris sugeneruoja kas bus kuris zaidejas ir issiuncia klientui jo player numeri(1 ctrl, 2 esc), arba lokaliam rezime padaro player 0
if option == '1':
    player = int(round(random.randint(90,200)/100.0))
    playerClient = 3 - player #SMART!
    clientSock.send(str(playerClient))
elif option == '2':
    player = int(serverSock.recv(1))
else:
    player = 0

#Serveris sugeneruoja skaiciu kuris bus determenistishkos funkcijos raktu(ziureti def obstacleGenerator(seed)) ir issiuncia klientui
if option == '1' or option == '4':
    seed = random.randint(1,500)
    if player != 0: clientSock.send(str(seed))
else:
    seed = int(serverSock.recv(3))

#Zaidejui pasakoma ka jis valdys ir kokiais mygtukais
if player == 1:
    print("\nYou are CTRL! W,S,q - quit")
    time.sleep(3)
elif player == 2:
    print("\nYou are ESC! /\,\/,q - quit")
    time.sleep(3)

initscr()
noecho()
curs_set(0)
win = newwin(20,70,0,0)
win.keypad(1)
win.nodelay(1)
win.border('|','|','-','-','+','+','+','+')

posBuf = ''                 #Saugomi gautos is kito zaidejo koordinates

pos1 = [8,14]               #Ctrl pradzios koordinates
ctrl1 = " ____ "
ctrl2 = "|    |"
ctrl3 = "|Ctrl|"
ctrl4 = "|____|"

pos2 = [8,40]               #Esc pradzios koordinates
esc1 = " ____ "
esc2 = "|    |"
esc3 = "|Esc |"
esc4 = "|____|"

chargeBar = ''              #parodo veikeju suolio i prieki intervala grafishkai

startTime = time.time()     #registruojamas laikas kad zinoti kada paleisti daugiau barjeru
moveInterval = 3            #sekundziu skaicius, kaip daznai i prieki juda veikejai
lastMove = startTime + 10   #sudaro 10 sekundziu perioda kai veikejai nejuda i prieki zaidimo pradzioje 

numOfObstacles = 10         #maksimalus kliuciu kiekis
numOfDeadObstacles = 0      #skaitiklis tam kad zinoti kiek jau kliuciu buvo sugeneruota, ribojasi numOfDeadObstaclesLimit(ziureti obstacleGenerator(seed))
numOfDeadObstaclesLimit = 3000 #limitas, parodo kiek kliuciu nesikartos
future = []                 #masyvas kuris laikys sugeneruotas kliuciu koordinates

#Determenistishka funkcija kuri naudojama duomenu srauto tarip serverio ir kliento sumazinimui, reikalingas tik vienas skaicius - sekla
def obstacleGenerator(seed):
    for i in range(0,numOfDeadObstaclesLimit):
        future.insert(0,int(((math.cos(i)*100)*seed))%14 +1) #sugeneruojami skaiciai kuri butu intervale (1,LAUKO_DYDIS(20)-2-FIGUROS_ILGIS(4))

#Paleidziamas generatorius
obstacleGenerator(seed)

#Metodas kuris pabaigia programos vykdyma, uzdaro portus, atjungia _curses aplinka, jeigu gaunamas signalas nuo kito kliento kad zaidimas jau baigesi
#tai zaidimas pereina i lokalu rezima ir pabaigia paskutini barieru prasukima ir tada pabaigia zaidima cia
def results(winResult):
    global option
    global player
    if winResult != 'end':
        if option == '1':
            clientSock.send('en')
            clientSock.close()
            serverSock.close()
        elif option == '2':
            serverSock.send('en')
            serverSock.close()
        time.sleep(2)
        endwin()
        if winResult == 'first':
            print "Player Ctrl wins!"
        elif winResult == 'second':
            print "Player Esc wins!"
        elif winResult == 'quit':
            print "The player has quit"
        exit()
    elif winResult == 'end':
        if option == '1':
            clientSock.close()
            serverSock.close()
        elif option == '2':
            serverSock.close()
        time.sleep(2)
        endwin()
        option = '4'
        player = 0

#Trina Ctrl pedsakus, animacijos dalis
def erase1():
    win.addstr(pos1[0]+0,pos1[1],"      ")
    win.addstr(pos1[0]+1,pos1[1],"      ")
    win.addstr(pos1[0]+2,pos1[1],"      ")
    win.addstr(pos1[0]+3,pos1[1],"      ")

#Paiso nauja Ctrl pozicija, animacijos dalis
def draw1():
    win.addstr(pos1[0]+0,pos1[1],ctrl1)
    win.addstr(pos1[0]+1,pos1[1],ctrl2)
    win.addstr(pos1[0]+2,pos1[1],ctrl3)
    win.addstr(pos1[0]+3,pos1[1],ctrl4)

#Trina Esc pedsakus, animacijos dalis
def erase2():
    win.addstr(pos2[0]+0,pos2[1],"      ")
    win.addstr(pos2[0]+1,pos2[1],"      ")
    win.addstr(pos2[0]+2,pos2[1],"      ")
    win.addstr(pos2[0]+3,pos2[1],"      ")

#Paiso nauja Esc pozicija, animacijos dalis
def draw2():
    win.addstr(pos2[0]+0,pos2[1],esc1)
    win.addstr(pos2[0]+1,pos2[1],esc2)
    win.addstr(pos2[0]+2,pos2[1],esc3)
    win.addstr(pos2[0]+3,pos2[1],esc4)


#Kliuciu klase kur saugomi dinaminiai duomenys apie jas(veikejams nereikia nes ju tik 2, o barjeru gali buti daugiau nei 10)
class Barier:
    lifespan = 0                                   #Kiek kliuties objektas jau padare zingsniu
    posBarier = 0                                  #Klities padetis dabar
    elapsed = 0.0                                  #Laikas praejes nuo buvusio zingsnio(trivialus atributas)
    timeRedraw = 0                                 #Laikas kada buvo darytas praeitas zingsnis
    speed = 0                                      #Kliuties greitis, kiek 1sec/speed zingsniu padaroma i sekunde(neobjektyvus atributas del sleep()'u)
    
    #Kliuties perpesimas su patikrinimu ar reikia pastumti veikeja, ir ar kliutis isstums veikeja is zaidimo, ir ar susidurs veikejai, animacijos dalis
    def moveBarier(self):
        win.addch(self.posBarier[0]+0,self.posBarier[1],' ')
        win.addch(self.posBarier[0]+1,self.posBarier[1],' ')
        win.addch(self.posBarier[0]+2,self.posBarier[1],' ')
        win.addch(self.posBarier[0]+3,self.posBarier[1],' ')
        self.posBarier[1] -= 1
        for i in range(0,3):
            if self.posBarier[0]+i in range(pos1[0]-1,pos1[0]+4) and self.posBarier[1] == pos1[1]+5:
                if checkLoss1(): beep(); flash(); print "Ctrl has lost esc!"; beep(); results('second')
                erase1()
                pos1[1] -= 1
                draw1()
            if self.posBarier[0]+i in range(pos2[0]-1,pos2[0]+4) and self.posBarier[1] == pos2[1]+5:
                if checkLoss2(): beep(); flash(); print "Esc forgot the right way!"; beep(); results('first')
                if checkWin1(): beep(); flash(); print "Esc got too brave!"; beep(); results('first')
                erase2()
                pos2[1] -= 1
                draw2()
        win.addch(self.posBarier[0]+0,self.posBarier[1],'|')
        win.addch(self.posBarier[0]+1,self.posBarier[1],'|')
        win.addch(self.posBarier[0]+2,self.posBarier[1],'|')
        win.addch(self.posBarier[0]+3,self.posBarier[1],'|')

    #Metodas kvieciamas norint saveikauti su kliuties objektu, patikrina ar kliutis gali judeti, ar dar gali gyventi, kiek dar kliuciu galima sugeneruoti
    def calcBarier(self):
        global future
        global numOfDeadObstacles
        global numOfDeadObstaclesLimit
        self.elapsed = time.time() - self.timeRedraw
        if self.elapsed > self.speed :
            self.elapsed = 0.0
            self.timeRedraw = time.time()
            if self.lifespan < 68:                                  #68=70(lauko ilgis)-2
                self.moveBarier()
                self.lifespan += 1
        if self.lifespan >= 68:
            self.lifespan = 0
            self.posBarier = [future[numOfDeadObstacles],68]
            numOfDeadObstacles += 1
            self.speed = (future[numOfDeadObstacles]*2)/100.0
        if numOfDeadObstacles >= numOfDeadObstaclesLimit:
            numOfDeadObstacles = 0

obstacles = []                                                      #Masyvas kliutims laikyti

#Pirma kliuciu generacija
for i in range(0,numOfObstacles):
    obstacles.insert(0,Barier())
for i in range(0,numOfObstacles):
    obstacles[i].posBarier = [future[i*5],68]
for i in range(0,numOfObstacles):
    obstacles[i].speed = (future[i*5]*2)/100.0

#Patikrinimas ar Ctrl gali judeti i desine
def checkRight1():
    for i in range(0,4):
        if win.inch(pos1[0]+i,pos1[1]+6) == ord('|'):
            return False
    return True

#Patikrinimas ar Ctrl gali judeti i kaire(trivialus metodas, naudojamas testavime)
def checkLeft1():
    for i in range(0,4):
        if win.inch(pos1[0]+i,pos1[1]-1) != ord(' '):
            return False
    return True

#Patikrinimas ar Ctrl gali judeti i virsu
def checkUp1():
    for i in range(0,5):
        if win.inch(pos1[0]-1,pos1[1]+i) != ord(' '):
            return False
    return True

#Patikrinimas ar Ctrl gali judeti zemyn
def checkDown1():
    for i in range(0,5):
        if win.inch(pos1[0]+4,pos1[1]+i) != ord(' '):
            return False
    return True

#Patikrinimas ar Esc gali judeti i desine
def checkRight2():
    for i in range(0,4):
        if win.inch(pos2[0]+i,pos2[1]+6) == ord('|'):
            return False
    return True

#Patikrinimas ar Esc gali judeti i kaire(trivialus metodas, naudojamas testavime)
def checkLeft2():
    for i in range(0,4):
        if win.inch(pos2[0]+i,pos2[1]-1) != ord(' '):
            return False
    return True

#Patikrinimas ar Esc gali judeti i virsu
def checkUp2():
    for i in range(0,5):
        if win.inch(pos2[0]-1,pos2[1]+i) != ord(' '):
            return False
    return True

#Patikrinimas ar Esc gali judeti zemyn
def checkDown2():
    for i in range(0,5):
        if win.inch(pos2[0]+4,pos2[1]+i) != ord(' '):
            return False
    return True

#Patikrinimas ar Ctrl pateko uz lauko ribu
def checkLoss1():
    if (pos1[1] - 1) == 0:
        return True
    return False

#Patikrinimas ar Esc pateko uz lauko ribu(kairiuju)
def checkLoss2():
    if (pos2[1] - 1) == 0:
        return True
    return False

#Patikrinimas ar Ctrl liecia Esc po judejimo i prieki(apgalvota mechanikos dalis kad Esc turetu paskutini shansa pabegti)
def checkWin1():
    if pos1[0] in range(pos2[0],pos2[0]+3) and pos1[1]+5 == pos2[1]:
        return True
    return False

#Patikrinimas ar Esc liecia desiniaja lauko dali - laimi
def checkWin2():
    if pos2[1]+4 == 60:
        return True
    return False

#Isankstinis veikeju piesimas
draw1()
draw2()

key = ''    #Laiko klavishu paspaudimus
#Kol ne bus paspaustas 'q' arba neivyks viena is laimejimo/pralaimejimo salygu kartosis sis ciklas, faktiskai main metodas ir vykdomo kodo pradzia
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PRADZIA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
while key != ord('q'):
    win.refresh()

    #Periodinis kliuciu paisimas su kliuciu kiekio didejimu
    for i in range(0,numOfObstacles):
        obstacles[i].calcBarier()
        if i > (int(round((time.time() - startTime)))/5.0) - 1:
            break

    #Laimejimo salygu tikrinimas, veikeju judejimas i prieki
    if time.time() - lastMove > moveInterval:
        if checkWin1(): beep(); flash(); print "Ctrl has caught esc!"; beep(); results('first')
        if checkWin2(): beep(); flash(); print "Esc has escaped ctrl!"; beep(); results('second')
        if checkRight1():
            erase1()
            pos1[1] += 1
            draw1()
        if checkRight2():
            erase2()
            pos2[1] += 1
            draw2()
        lastMove = time.time()
        win.addstr(19,35,"   ")
    #Jeigu neivyksta judejimas, grafishkai atvaizduojama kada jis ivyks
    else:
        elapsed = time.time() - lastMove
        if elapsed < 0.5:
            chargeBar = '.     '
        elif elapsed < 1:
            chargeBar = '..    '
        elif elapsed < 1.5:
            chargeBar = '..x   '
        elif elapsed < 2:
            chargeBar = '..xx  '
        elif elapsed < 2.5:
            chargeBar = '..xxX '
        elif elapsed < 3:
            chargeBar = '..xxXX'
        win.addstr(19,27,"Charge: " + chargeBar)

    key = win.getch()
    #Zaideju inputo analizavimas, priklauso nuo tuo ar jie 1 ar 2 zaidejas, ir judejimo registravimas-issiuntimas klientui/serveriui
    if key == ord('w') and (player == 1 or player == 0) and checkUp1():
        erase1()
        pos1[0] -= 1
        draw1()
        if option == '1':
            clientSock.send(str(pos1[0]))
        elif option == '2': serverSock.send(str(pos1[0]))
    elif key == ord('s') and (player == 1 or player == 0) and checkDown1():
        erase1()
        pos1[0] += 1
        draw1()
        if option == '1':
            clientSock.send(str(pos1[0]))
        elif option == '2': serverSock.send(str(pos1[0]))

    elif key == KEY_UP and (player == 2 or player == 0) and checkUp2():
        erase2()
        pos2[0] -= 1
        draw2()
        if option == '1':
            clientSock.send(str(pos2[0]))
        elif option == '2': serverSock.send(str(pos2[0]))
    elif key == KEY_DOWN and (player == 2 or player == 0) and checkDown2():
        erase2()
        pos2[0] += 1
        draw2()
        if option == '1':
            clientSock.send(str(pos2[0]))
        elif option == '2': serverSock.send(str(pos2[0]))

    #Jeigu nera ivesties, siunciami tusti pranesimai kad kitame gale nebutu laukimo ir uzsiciklintos tylos
    else:
        if option == '1':
            clientSock.send("  ")
        elif option == '2':
            serverSock.send("  ")

    #Gaudoma kito zaidejo ivestis, jeigu gautas pranesimas "qu" skaitoma kad kitas zaidejas paliko zaidima
    if player == 1:
        if option == '1':
            posBuf = clientSock.recv(2)
            if posBuf != "  " and posBuf != " " and posBuf and posBuf != "qu" and posBuf != "en" and int(posBuf) != 0:
                erase2()
                pos2[0] = int(posBuf)
                draw2()
        else:
            posBuf = serverSock.recv(2)
            if posBuf != "  " and posBuf != " " and posBuf and posBuf != "qu" and posBuf != "en"  and int(posBuf) != 0:
                erase2()
                pos2[0] = int(posBuf)
                draw2()
    elif player == 2:
        if option == '1':
            posBuf = clientSock.recv(2)
            if posBuf != "  " and posBuf != " " and posBuf and posBuf != "qu" and posBuf != "en"  and int(posBuf) != 0:
                erase1()
                pos1[0] = int(posBuf)
                draw1()
        else:
            posBuf = serverSock.recv(2)
            if posBuf != "  " and posBuf != " " and posBuf and posBuf != "qu" and posBuf != "en"  and int(posBuf) != 0:
                erase1()
                pos1[0] = int(posBuf)
                draw1()

    #Zaidimo palikimo registracija ir isejimas
    if option != '4' and posBuf == "qu":
        print "The player has quit."
        time.sleep(2)
        results('quit')
    else:
        #Jei zaidimas jau pasibaige kitam zaidejui apdorojams sis signalas
        if posBuf == "en":
            results("end")
    posBuf=''
    time.sleep(0.01) #laiko pauze :)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PAGRINDINIO CIKLO PABAIGA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

endwin()

#Isejimo atveju pranesimas kitam zaidejui apie isejima ir Kultura
if option == '1':
    clientSock.send("qu")
    time.sleep(1)
    clientSock.close()
    serverSock.close()
elif option == '2':
    serverSock.send("qu")
    time.sleep(1)
    serverSock.close()

#MADE BY MARK GANUSEVICH AND ERIK KISEL, 2013