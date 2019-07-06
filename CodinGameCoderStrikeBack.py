import math
import sys
from copy import deepcopy
import random


thetaSubD=4 #MUST BE EVEN
powerSubD=2

class Vector:
    def __init__(self,x,y):
        self.x=x
        self.y=y
    
    def __add__(self,v):
        out=Vector(self.x+v.x,self.y+v.y)
        return out
        
    def __neg__(self):
        out=Vector(-1*self.x,-1*self.y)
        return out
    
    def __sub__(self,v):
        out=self+(-v)
        return out
        
    def __str__(self):
        return str(self.x)+" "+str(self.y)
        
    def __abs__(self):
        return math.sqrt(self.x*self.x+self.y*self.y)
        
    def __mul__(self,scal):
        out=Vector(self.x*scal,self.y*scal)
        return out
        
    def __mod__(self,v):#produit scalaire
        return self.x*v.x+self.y*v.y
        
    def __floor__(self):
        out=Vector(math.floor(self.x),math.floor(self.y))
        return out
        
    def __round__(self):
        out=Vector(round(self.x),round(self.y))
        return out
        
    def __eq__(self,v):
        return self.x==v.x and self.y==v.y

    def __trunc__(self):
        out=Vector(math.trunc(self.x),math.trunc(self.y))
        return out
        
    def angle(self):
        return math.atan2(self.y,self.x)*180/math.pi
        
    def unitaire(self):
        out=Vector(self.x,self.y)
        out=out*(1.0/abs(out))
        return out

def normalize(x):
    """x en degres"""
    if x>360:
        return normalize(x-360)
    elif x>180:
        return x-360
    elif x<-360:
        return normalize(x+360)
    elif x<-180:
        return x+360
    else:
        return x

def directeur(angle):
    """angle en degre"""
    theta=math.radians(angle)
    out=Vector(math.cos(theta),math.sin(theta))
    return out
    
    
class Pod:
    def __init__(self,checkpoints):
        self.checkpoints=checkpoints
        self.pos=Vector(0,0)
        self.v=Vector(0,0)
        self.angle=0
        self.nextCpId=0
        self.lap=1
        
        self.boostUsed=False
        self.output=[0,100]
        self.maxDist=max([abs(checkpoints[i]-checkpoints[i+1]) for i in range(len(checkpoints)-1)]+[abs(checkpoints[0]-checkpoints[-1])])
        self.needInit=True
    
    def update(self,x,y,vx,vy,angle,nextCpId):
        self.pos.x=x
        self.pos.y=y
        self.v.x=vx
        self.v.y=vy
        self.angle=angle
        if self.nextCpId!=0 and nextCpId==0:
            self.lap+=1
        self.nextCpId=nextCpId
        
        if self.needInit:
            self.needInit=False
            self.output=[normalize((self.checkpoints[self.nextCpId]-self.pos).angle()-self.angle),100]
    
    def send(self):
        print(str(round(self.pos+(directeur(self.angle+self.output[0])*100)))+" "+str(self.output[1]))
             
def collisionTime(pos1, v1, pos2, v2, radius):
	r = radius*radius;

	v = v1-v2;
	p21 = pos1-pos2;

	if v.x == 0 and v.y == 0:
		return 10000;

	a = v%v;
	b = v%p21 * 2
	if b >= 0:
		return 10000
	c = p21%p21 - r

	d = b*b - 4 * a*c
	if d<0:
		return 10000

	return (-b - math.sqrt(d)) / (2 * a)


def possibleOutput(pod):
    """don't manage shield and boost"""
    deltaThetaS=[-18 +36/thetaSubD*i for i in range(thetaSubD+1)]
    powerS=[round(i/powerSubD*100) for i in range(powerSubD+1)]
    return [[deltaTheta,power] for deltaTheta in deltaThetaS for power in powerS]

def generateCp(n):
    out=[]
    for i in range(n):
        out.append(Vector(random.randint(0,16000),random.randint(0,9000)))
    return out

def cap(x,m,M):
    if x<m:
        return m
    elif x>M:
        return M
    else:
        return x

def simulate1Step(pod):
    """doesn't take collision into account"""
    pod.angle=pod.angle+cap(pod.output[0],-18,18)
    pod.v+=directeur(pod.angle)*pod.output[1]
    pod.pos+=pod.v
    pod.v=math.trunc(pod.v*0.85)
    pod.pos=round(pod.pos)
    if collisionTime(pod.pos, pod.v, pod.checkpoints[pod.nextCpId], Vector(0,0), 595) < 1:
        last=pod.nextCpId
        pod.nextCpId=(pod.nextCpId+1)%len(pod.checkpoints)
        if pod.nextCpId==0 and last!=0:
            pod.lap+=1


def evaluate(pod):
    reachPoint=pod.lap*10 + pod.nextCpId + math.exp(-1*abs(pod.checkpoints[pod.nextCpId]-pod.pos)/4000.0)
    return reachPoint

anticipation=2
def findBestMove(pod,iter):
    if iter==1:
        moves=possibleOutput(pod)
        bestMove=moves[0]
        bestScore=0
        for move in moves:
            testPod=deepcopy(pod)
            testPod.output=move
            for _ in range(anticipation):
                simulate1Step(testPod)
        
            x=evaluate(testPod)
            if x>bestScore:
                bestScore=x
                bestMove=deepcopy(move)
        return (bestMove,bestScore)
    else:

        moves=possibleOutput(pod)
        bestMove=moves[0]
        bestScore=0
        for move in moves:
            testPod=deepcopy(pod)
            testPod.output=move
            for _ in range(anticipation):
                simulate1Step(testPod)
            x=evaluate(testPod)
            bestMoveAfter,bestScoreAfter=findBestMove(testPod,iter-1)
            x+=bestScoreAfter
            
            if x>bestScore:
                bestScore=x
                bestMove=deepcopy(move)

        return (bestMove,x)

laps = int(input())
checkpoint_count = int(input())
checkpoints=[]
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    checkpoints.append(Vector(checkpoint_x,checkpoint_y))

myPods=[]
myPods.append(Pod(checkpoints))
myPods.append(Pod(checkpoints))
hisPods=[]
hisPods.append(Pod(checkpoints))
hisPods.append(Pod(checkpoints))


# game loop
while True:
    for i in range(2):
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        myPods[i].update(x, y, vx, vy, angle, next_check_point_id)
        
    for i in range(2):
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]
        hisPods[i].update(x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2)
        
    for i in range(2):
        myPods[i].output=findBestMove(myPods[i],2)[0]
        print(myPods[i].output,file=sys.stderr)
        myPods[i].send()
