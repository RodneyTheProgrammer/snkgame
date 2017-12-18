#!/usr/bin/env python
import curses
import time
import random
from operator import getitem,attrgetter
stdscr = curses.initscr()
L,W= stdscr.getmaxyx()
curses.start_color()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
stdscr.keypad(1)
L,W = stdscr.getmaxyx()
normal,infiltrate,get2goal,runaway=0,1,2,3
def start_page(window):
    maxy,maxx = window.getmaxyx()
    s =  'Snake'
    paktc = 'Press any key to continue'
    window.addstr(maxy/2,maxx/2-len(s)/2,s,curses.A_BOLD)
    window.addstr(maxy/2+1,maxx/2-len(paktc)/2,paktc)
    window.refresh()
    window.getch()
    window.erase()
def MID(L,D): #move in direction
    R =L.copy()
    if D == 360:
        return R
    if 0<D<180:
        R.y = R.y-1
    elif 180 < D < 360 :
        R.y = R.y+1
    if 90 < D < 270:
        R.x = R.x-1
    elif 270 < D or D< 90:
        R.x = R.x+1
    return R
#point-related stuff

class point(object):
    def __init__(self,y,x):
        self.y =y
        self.x =x
    def __cmp__(self,other):
        if self.x == other.x and self.y == other.y :
            return 0
        else:
            return -1
    def __str__(self):
        return str((self.y,self.x))
    def __repr__(self):
        return str(self)
    def copy(self):
        return point(self.y,self.x)

def pointgen(L,W):
    x = point(0,0)
    x.y=random.randint(0+1,L-2)
    x.x=random.randint(0+1,W-2)
    return x

class dummy(object):
    def __init__(self,char,location=point(1,1)):
        self.location=location
        self.char=char
    def draw(self,window):
        window.addstr(self.location.y,self.location.x,self.char)
#living animals
class man(object):
    def __init__(self):
        self.score = 0
        self.location=point(1,1)
    def move(self,D):
        X = MID(self.location,D)
        if X.y != 0 and X.x != 0:
            if X.y != L-1 and X.x != W-1:
                self.location = X
    def live(self):
        pass
    def chance(self):
        return chance((500-self.score)/5)

    def draw(self,window):
        window.addstr(self.location.y,self.location.x,'@')

class rat(object):
    def __init__(self,coin,dude):
        self.master = dude
        self.coin = coin
        self.location = pointgen(L,W)
        self.attached=False
        self.previous_escape=45
        self.phase=normal
    def move(self,D):
        X = MID(self.location,D)
        if X.y != 0 and X.x != 0:
            if X.y !=L-1 and X.x != W-1:
                   self.location = X 
                   return True
        return False

    def draw(self,window):
        window.addstr(self.location.y,self.location.x,'r',curses.A_REVERSE)
    def live(self,snakes):
        rat = self.location
        snk = nearest_snake(snakes,rat).pieces[-1]
        threats = danger_directions(snakes,rat)
        sdistance = distance(rat,snk)
        isPhase = self.isPhase
        self.isAttached()
        escape = False
        if isPhase(infiltrate):
            if not self.goal in threats:
                self.phase = normal
            else:
                escape = True
                d = closest(self.goal)[0]

        if isPhase(runaway):
            if sdistance > 8:
                self.phase = normal

        if sdistance <= 8:
            if isPhase(runaway):
                escape = True
                if self.previous_escape not in threats:
                    d = self.previous_escape
                else:
                    d = opposite(direction(rat,snk))
            elif sdistance <= 4:
                escape = True
                if isPhase(infiltrate):
                     d = closest(self.previous_escape)[0]
                else:
                    if self.previous_escape not in threats:
                        d = self.previous_escape
                    d = opposite(direction(rat,snk))
                self.phase = runaway

        if isPhase(normal):
            self.phase = get2goal

        if self.phase == get2goal and self.goal() == direction(rat,snk):
            self.phase = infiltrate
            escape = True
            d = closest(self.goal())[0]

        if self.phase == get2goal:
            d = self.goal()
        if self.goal() == 360:
            self.attached = True

        if not self.move(d) :
            s = closest(d)
            for n in s:
                d = n
                if self.move(d):
                    break
        if self.attached:
            self.coin.location = MID(self.location,d)
        if escape :
              self.previous_escape = d
    def isAttached(self):
        if distance(self.location,self.coin.location) > 1:
            self.attached = False
    def isPhase(self,phase):
        if self.phase == phase:
            return True
        else:
            return False
    def goal(self):
        if self.attached:
            return direction(self.location,self.master.location)
        else:
            return direction(self.location,self.coin.location)
    def chance(self):
        return chance((500-self.master.score)/5)
        
class snake(object):
    def __init__(self):
        self.lenght=random.randint(3,7)
        self.pieces=[point(1,1)]
    def move(self,D):
        X=MID(self.pieces[-1],D)
        if X.y != 0 and X.x != 0:
            if X.y!= L-1 and X.x !=W-1:
                self.pieces.append(X)
                if len(self.pieces) > self.lenght:
                      del(self.pieces[0])
                return True
               
    def draw(self,window):
        for p in self.pieces:
            window.addstr(p.y,p.x,'s')
        p = self.pieces[-1]
        window.addstr(p.y,p.x,'S')

    def live(self,dude,pact,rats):
        m = dude.location
        snk = self.pieces[-1]

        l = pact[0]
        ldng = l.pieces[-1]
        h = distance(ldng,m)
        k = distance(snk,ldng)

        
        if self !=l and h < 5 and k < 14 :
                d = opposite(direction(snk,ldng))

        elif dude.chance():
                d= random.randint(0,8)*45
        else:
             d= direction(snk,m)

        if not self.move(d) :
            for n in closest(d):
                if self.move(n):
                    break

        if  m in self.pieces:
            snakeeaten(m,stdscr)
            if type(dude)==rat:
                del(rats[rats.index(dude)])
                return False
            else:
                return True
            self.lenght= self.lenght+1

def danger_directions(snakes,target):
    ret=[]
    for s in snakes:
        ret.append(direction(target,s.pieces[-1]))
    return ret  
def nearest_snake(_snakes,target):
        snakes = _snakes[:]
        a = map(getitem,map(attrgetter('pieces'),snakes),[-1]*len(snakes))
        b = map(distance,a,[target]*len(snakes))
        nearest = b.index(sorted(b)[0])
        return snakes[nearest]

def direction(point,target):
    if point.x > target.x:
        if point.y > target.y:
            return 135
        if point.y == target.y:
            return 180
        if point.y < target.y:
            return 225
    if point.x == target.x:
        if point.y > target.y:
            return 90
        if point.y == target.y:
            return 360
        if point.y < target.y:
            return 270
    if point.x < target.x:
        if point.y > target.y:
            return 45
        if point.y == target.y:
            return 0
        if point.y < target.y:
            return 315
def angle_delta(angle1,angle2):
    return abs(angle1-angle2)
def opposite(drctn):
    if drctn == 360:
        return 360
    else :
        return closest(drctn)[-1]

def distance(point,target):
    return int(((point.x-target.x)**2+(point.y-target.y)**2)**0.5)

def closest(drctn):
    if drctn == 360:
        return [360]
    l = []
    append = l.append
    a,b = drctn,drctn
    x = 1
    while a != b or x:
        if x:
            x=not x
        a = a + 45
        b = b - 45
        if b < 0:
            b = 315
        if  a == 360:
            a= 0
        append(a)
        append(b)
    return l


          
def drw_ln(r,D,L,win,m='#'):
       h=L
       c=0
       while c!=r:
           try:
               win.addstr(h.y,h.x,m)
           except:
               pass
           h = MID(h,D)
           c=c+1

def drw_sqr(r,location,window):
    _1=point(location.y-r/2,location.x-r/2)
    drw_ln(r,0,_1,window)
    drw_ln(r,270,_1,window)
    _2=point(location.y+r/2,location.x+r/2)
    drw_ln(r,180,_2,window)
    drw_ln(r,90,_2,window)
def gatelight(location,window):
    c=0
    while c != 6:
        time.sleep(0.05)
        drw_sqr(c,location,window)
        window.refresh()
        c=c+1

def snakefoo(location,lenght,window):
    window.addstr(location.y-1,location.x-1,'0-0')
    window.addstr(location.y,location.x-1,'\\_/')
    window.refresh()
    time.sleep(0.5)
    window.addstr(location.y-1,location.x-1,'>-<')
    window.addstr(location.y,location.x-1, '\\_/')
    window.refresh()
    time.sleep(0.2)
    c = 1
    while c <= lenght:
        window.addstr(location.y+c,location.x,'^')
        if c>=2:
          window.addstr(location.y+c-1,location.x,'|')
        window.refresh()
        c = c+1
        time.sleep(0.2)
    while 1 <= c:
        window.addstr(location.y+c,location.x,' ')
        if c == 2:
            window.addstr(location.y+c-1,location.x,'^')
        window.refresh()
        c = c-1
        time.sleep(0.2)


    window.addstr(location.y-1,location.x-1,'0-0')
    window.addstr(location.y,location.x-1, '\\_/')
    window.refresh()
    time.sleep(2.5)
       

def sparkle(location,window):
    window.addstr(location.y,location.x,'*')
    window.refresh()
    time.sleep(0.2)
    window.addstr(location.y-1,location.x-1,'\\|/')
    window.addstr(location.y,location.x-1,'- -')
    window.addstr(location.y+1,location.x-1,'/|\\')
    window.refresh()

def snakeeaten(location,window):
   
    window.addstr(location.y-1,location.x-1,'/-\\')
    window.addstr(location.y,location.x-1,  '.@.')
    try:
     window.addstr(location.y+1,location.x-1,'\\-/')
    except:
        pass
    window.refresh()
    c=0
    while c != 10:
        time.sleep(0.1)
        if c % 2 == 1:
            window.addstr(location.y,location.x,'@')
            window.refresh()
        else:
            window.addstr(location.y,location.x,' ')
            window.refresh()
        c = c+1
    window.addstr(location.y-1,location.x-1, '0_0')
    window.addstr(location.y,location.x-1,  '\\_/')
    window.addstr(location.y+1,location.x-1,'   ')
    window.refresh()
    time.sleep(0.5)
    window.addstr(location.y-1,location.x-1,'-')
    window.refresh()
    time.sleep(0.5)
    window.addstr(location.y-1,location.x-1,'0')
    window.refresh()
    time.sleep(0.5)
def snakestare(snakes,window):
    locations=[]
    for s in snakes:
        locations.append(s.pieces[-1])
    for l in locations:
        window.addstr(l.y-1,l.x-1,'0_0!!')
        window.addstr(l.y,l.x-1,'\\_/')
        window.refresh()
    time.sleep(1)
    c=0
    while c != 22:
        for l in locations:
            if c%2:
                window.addstr(l.y-1,l.x-1,'0_0  ')
            else:
                window.addstr(l.y-1,l.x-1,'-_-')
        window.refresh()
        time.sleep(0.1)
        c=c+1
    time.sleep(1.5)
def snakehappy(snakes,target,window):
    ls=[]
    for s in snakes:
        ls.append(s.pieces[-1])
    for l in ls:
        window.addstr(l.y-1,l.x-1,'0-0')
        window.addstr(l.y,l.x-1,'\\_/')
    window.refresh()
    time.sleep(0.2)
    for l in ls:
        window.addstr(l.y-1,l.x-1,'^-^')
    window.refresh()
    time.sleep(1)
        

def chance(percent):
    if percent < 4:
       percent = 4
    x = random.randint(1,100)
    if x <= percent:
        return True
    else:
        return False

def border(window):
    maxy,maxx=L,W
    maxx=maxx-1
    maxy=maxy-1
    _0 = point(0,0)
    drw_ln(maxy,270,_0,window,'|')
    drw_ln(maxx,0,_0,window,'-')
    _M= point(maxy,maxx)
    drw_ln(maxy,90,_M,window,'|')
    drw_ln(maxx,180,_M,window,'-')
    window.addstr(0,0,'+')
    window.addstr(0,maxx,'+')
    window.addstr(maxy,0,'+')
    window.addstr(maxy-1,maxx,'+')
def windowsave(window):
    while curses.is_term_resized(L,W):
        maxx,maxy=stdscr.getmaxyx()
        if maxx < W or maxy < L:
           stdscr.addstr(0,0,'Please resize the window',curses.A_BOLD)
           stdscr.refresh()
           time.sleep(0.5)

def TheGame(window):
    tb = dummy('',point(0,0))
    dude = man()
    dude.location = pointgen(L,W)
    snakes=[snake(),snake(),snake()]
    dude.location=pointgen(L,W)
    rats = []
    reached300=False
    Q=map(ord,('Q','q'))
    R=map(ord,('R','r'))
    for s in snakes:
        s.pieces[0]=pointgen(L,W)
        while s.pieces[0] == dude.location:
            s.pieces[0]=pointgen(L,W)
    coin = dummy('$',pointgen(L,W))
    gate = dummy('#',pointgen(L,W))
    while gate.location == coin.location:
        gate.location = pointgen(L,W)
    input=''
    while 1:
        if dude.score >= 300:
            reached300 = True
        window.erase()
        there_are_rats= len(rats)>0
        try:
           border(window)
           for s in snakes:
               s.draw(window)
           if there_are_rats:
             for r in rats:
               r.draw(window)
           dude.draw(window)
           gate.draw(window)
           coin.draw(window)
           tb.draw(window)
           window.refresh()
        except:
           windowsave(window)
        if len(rats) >= 1:
            rats[-1].live(snakes)
            for r in rats[:-1]:
                r.move(random.randint(0,8)*45)

        input = window.getch() 
        if input == curses.KEY_UP:
            dude.move(90)
        if input == curses.KEY_DOWN:
            dude.move(270)
        if input == curses.KEY_LEFT:
            dude.move(180)
        if input == curses.KEY_RIGHT:
            dude.move(0)
        if input in Q:
            tb.char='chicken heart!'
            tb.draw(window)
            window.refresh()
            snakestare(snakes,window)
            return (0,dude.score)
        if input in R:
           if reached300 and dude.score >= 200:
            dude.score=dude.score-200
            tb.char='real food!'
            tb.draw(window)
            window.refresh()
            rats.append(rat(coin,dude))
            sparkle(rats[-1].location,window)
            window.addstr(rats[-1].location.y,rats[-1].location.x,'r')
            snakehappy(snakes,rats[-1].location,window)

        for s in snakes:
            if len(rats) > 0 :
                h=rats[-1]
            else:
                h=dude
            if s.live(h,snakes,rats) == True:
                return (-1,dude.score)

        if dude.location == coin.location:
            dude.score =dude.score+int(3000*(1.0/(W+L)))
            tb.char=str(dude.score)+'$'
            coin.location=pointgen(L,W)
        if dude.location == gate.location:
            gatelight(gate.location,window)
            snakestare(snakes,window)
            return (1,dude.score)
            break
start_page(stdscr)
x=TheGame(stdscr)
stdscr.erase()
curses.nocbreak(),curses.echo(),curses.endwin(),curses.endwin()

if x[0]==-1:
    print "You\'ve been eaten with %s grams of gold you found"%x[1]
if x[0]==0:
    print "You left the game embarrassingly while having only %s grams of gold"%x[1]
if x[0] == 1:
    print "You escaped with %s grams of gold"%x[1]
