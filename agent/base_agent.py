import random
import pygame
import sys
from pygame.constants import MOUSEBUTTONDOWN, MOUSEMOTION
from reversi import Reversi
import time

class BaseAgent():
    def __init__(self, color = "black", rows_n = 8, cols_n = 8, width = 600, height = 600):
        self.color = color
        self.rows_n = rows_n
        self.cols_n = cols_n
        self.block_len = 0.8 * min(height, width)/cols_n
        self.col_offset = (width - height)/2 + 0.1 * min(height, width) + 0.5 * self.block_len
        self.row_offset = 0.1 * min(height, width) + 0.5 * self.block_len
        
    def step(self, reward, obs):
        """
        Parameters
        ----------
        reward : dict
            current_score - previous_score
            
            key: -1(black), 1(white)
            value: numbers
            
        obs    :  dict 
            board status

            key: int 0 ~ 63
            value: [-1, 0 ,1]
                    -1 : black
                     0 : empty
                     1 : white

        Returns
        -------
        tuple:
            (x, y) represents position, where (0, 0) mean top left. 
                x: go right
                y: go down
        event_type:
            non human agent uses pygame.USEREVENT
        """

        raise NotImplementError("You didn't finish your step function. Please override step function of BaseAgent!")
    
class HumanAgent(BaseAgent):
    def step(self, reward, obs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                return event.pos, event.type
            if event.type == pygame.MOUSEBUTTONDOWN:
                return event.pos, pygame.USEREVENT

        return (-1, -1), None

class RandomAgent(BaseAgent):
    #改成從可下步伐中隨機抽出
    def step(self, reward, obs):
        move = []
        for i in range(64):
            can = self.can_place(obs,i,self.color)
            if can ==True:
                move.append(i)
        p = random.randint(0,len(move)-1)
        return (self.col_offset + (move[p]%8) * self.block_len, self.row_offset + (move[p]//8) * self.block_len), pygame.USEREVENT

    def can_place(self,obs,place,color):

        '''
        確認周遭九宮格中是否有敵手的旗子

        Parameter
        ------------------------
        obs : dict
        棋盤戰況

        place : int
        要測試是否能放的點

        color : str
        我方顏色
        '''

        if obs[place]!=0:
            return False
        x=place%8
        y=place//8
        sc=1
        if color == 'black': 
            sc = -1
        is_avail = False
        for i in range(-1, 2):
            if x+i < 0 or x+i > 7: continue
            for j in range(-1, 2):
                if y+j < 0 or y+j > 7: continue
                if obs[x+i+(y+j)*8] == -1 * sc:
                    if self.check_direction(x, y, i, j,obs,sc):
                        is_avail = True
        return is_avail
    
    def check_direction(self,row,col,dx,dy,obs,sc,flip=False):
        '''    
        測試輸入點在輸入方向是否有我方旗子一同夾住敵手旗子

        Parameter
        ------------------------
        row : int
        測試點x軸

        col : int
        測試點y軸

        dx : int
        測試方向x分量

        dy : int
        測試方向y分量

        obs : dict
        棋盤戰況

        sc : int 
        我方顏色代碼
        -1 : black
        1 : white

       ''' 
        is_avail = False
        x, y = [dx], [dy]
        while 0 <= row+x[-1] < 8 and 0 <= col+y[-1] < 8:
            label = row+x[-1]+8*(col+y[-1])
            if obs[label]==0:
                break
            if obs[label] == sc:
                return True
            x.append(x[-1] + dx)
            y.append(y[-1] + dy)
        return is_avail


'''
#-------------------------------------------------------
#old random written by TA
#-------------------------------------------------------

class RandomAgent(BaseAgent):
    def step(self, reward, obs):
        
        return (self.col_offset + random.randint(0, self.cols_n-1) * self.block_len, self.row_offset + random.randint(0, self.rows_n-1) * self.block_len), pygame.USEREVENT
     '''

class MyAgent(BaseAgent):
    def step(self, reward, obs):
        move = []
        sc,maxi,maxii = 1,0,0
        if self.color == 'black': 
            sc = -1
        for i in range(64):
            can = self.can_place(obs,i,sc)
            if can ==True:
                move.append(i)
        for i in move:
            k = self.flip_or_not(i%8,i//8,obs,sc)
            ans = self.how_many(k,sc)
            if ans>maxi:
                maxi=ans
                maxii=i
            if ans==maxi and random.randint(0,1)==1:
                maxi=ans
                maxii=i

        return (self.col_offset + (maxii%8) * self.block_len, self.row_offset + (maxii//8) * self.block_len), pygame.USEREVENT

    def flip_or_not(self,x,y,obs,sc):
        ans = obs.copy()
        ans[x+8*y] = sc
        for i in range(-1, 2):
            if x+i < 0 or x+i > 7: continue
            for j in range(-1, 2):
                if y+j < 0 or y+j > 7: continue
                if obs[x+i+(y+j)*8] == -1 * sc:
                    ans = self.flip_it(x, y, i, j,ans,sc)
        return ans
                              
    def can_place(self,obs,place,sc):
        '''
        確認周遭九宮格中是否有敵手的旗子

        Parameter
        ------------------------
        obs : dict
        棋盤戰況

        place : int
        要測試是否能放的點

        color : str
        我方顏色

        '''
        if obs[place]!=0:
            return False
        x=place%8
        y=place//8
        is_avail = False
        for i in range(-1, 2):
            if x+i < 0 or x+i > 7: continue
            for j in range(-1, 2):
                if y+j < 0 or y+j > 7: continue
                if obs[x+i+(y+j)*8] == -1 * sc:
                    if self.check_direction(x, y, i, j,obs,sc):
                        is_avail = True
        return is_avail
    
    def check_direction(self,row,col,dx,dy,obs,sc,flip=False):
        '''
        測試輸入點在輸入方向是否有我方旗子一同夾住敵手旗子

        Parameter
        ------------------------
        row : int
        測試點x軸

        col : int
        測試點y軸

        dx : int
        測試方向x分量

        dy : int
        測試方向y分量

        obs : dict
        棋盤戰況

        sc : int 
        我方顏色代碼
        -1 : black
         1 : white
        '''
        is_avail = False
        x, y = [dx], [dy]
        while 0 <= row+x[-1] < 8 and 0 <= col+y[-1] < 8:
            label = row+x[-1]+8*(col+y[-1])
            if obs[label]==0:
                break
            if obs[label] == sc:
                if flip:
                    ans = obs.copy()
                    for r, c in zip(x, y):
                        ans[row+r+8*(col+c)]=sc
                    return ans
                return True
            x.append(x[-1] + dx)
            y.append(y[-1] + dy)
        return is_avail

    def how_many(self,want,sc):
        k=0
        for i in range(64):
            if want[i]==sc:
                k+=1
        return k

    def flip_it(self,row,col,dx,dy,obs,sc):
        ans = obs.copy()
        x, y = [dx], [dy]
        while 0 <= row+x[-1] < 8 and 0 <= col+y[-1] < 8:
            label = row+x[-1]+8*(col+y[-1])
            if obs[label]==0:
                break
            if obs[label] == sc:
                for r, c in zip(x, y):
                    ans[row+r+8*(col+c)]=sc
                '''
                print('\nrow = ',row,'  col = ',col,'\n')
                for i in range(8):
                    print(ans[i*8],ans[i*8+1],ans[i*8+2],ans[i*8+3],ans[i*8+4],ans[i*8+5],ans[i*8+6],ans[i*8+7],sep = '  ')
                print('\n')
                for i in range(8):
                    print(obs[i*8],obs[i*8+1],obs[i*8+2],obs[i*8+3],obs[i*8+4],obs[i*8+5],obs[i*8+6],obs[i*8+7],sep = '  ')
                print('\n')
                '''
                return ans
            x.append(x[-1] + dx)
            y.append(y[-1] + dy)
        return ans

class MyAgent_2(MyAgent):
    def step(self, reward, obs):
        move = []
        reval_move=[]
        k={}
        sc,maxi,maxii = 1,100,0
        if self.color == 'black': 
            sc = -1
        for i in range(64):
            can = self.can_place(obs,i,sc)
            if can ==True:
                move.append(i)
        for i in move:
            k = self.flip_or_not(i%8,i//8,obs,sc)
            reval_move=[]
            for n in range(64):
                reval_place = self.can_place(k,n,sc*(-1))
                if reval_place:
                    reval_move.append(n)
            if len(reval_move) < maxi:
                maxi = len(reval_move)
                maxii = i
            if len(reval_move)==maxi and random.randint(0,1)==1:
                maxi = len(reval_move)
                maxii = i
        return (self.col_offset + (maxii%8) * self.block_len, self.row_offset + (maxii//8) * self.block_len), pygame.USEREVENT

class MyAgent_3(MyAgent):
    def step(self, reward, obs):
        move = []
        reval_move=[]
        k={}
        sc,maxi,maxii = 1,0,0
        comp=[]
        if self.color == 'black': 
            sc = -1
        for i in range(64):
            can = self.can_place(obs,i,sc)
            if can ==True:
                move.append(i)
        for i in move:
            k = self.flip_or_not(i%8,i//8,obs,sc)
            reval_move=[]
            for n in range(64):
                reval_place = self.can_place(k,n,sc*(-1))
                if reval_place:
                    reval_move.append(n)
            for l in reval_move:
                k = self.flip_or_not(l%8,l//8,k,sc*(-1))
                cout = self.how_many(k,sc*(-1))
                if cout>maxi:
                    maxi = cout
                if cout == maxi and random.randint(0,1)==1:
                    maxi = cout
            comp.append(maxi)
        haha = min(comp)
        n=0
        for i in comp:
            if i == haha:
                lll = n
            n+=1
        maxii = move[lll]
        return (self.col_offset + (maxii%8) * self.block_len, self.row_offset + (maxii//8) * self.block_len), pygame.USEREVENT

class MyAgent_Tobbys(MyAgent):
    def step(self, reward, obs):#4
        sc = 1
        move_list,areas_list,steep_list = [],[],[]
        bad_move = [1,6,8,9,14,15,48,49,54,55,57,62]
        good_move = [2,3,4,5,16,23,24,31,32,39,40,47,58,59,60,61]
        if self.color == 'black': 
            sc = -1
        move=[]
        steeeps = 0

        for i in [0,7,63,56]:
            can = self.can_place(obs,i,sc)
            if can :
                move.append(i)
        if move!=[]:
            anss = move[random.randint(0,len(move)-1)]
            if anss == 0:
                for i in [1,8,9]:
                    bad_move.remove(i)
                for i in [1,8]:
                    good_move.append(i)
            elif anss == 7:
                for i in [6,14,15]:
                    bad_move.remove(i)
                for i in [6,15]:
                    good_move.append(i)
            elif anss == 56:
                for i in [48,49,57]:
                    bad_move.remove(i)
                for i in [48,57]:
                    good_move.append(i)
            else:
                for i in [54,55,62]:
                    bad_move.remove(i)
                for i in [55,62]:
                    good_move.append(i)
            return (self.col_offset + (anss%8) * self.block_len, self.row_offset + (anss//8) * self.block_len), pygame.USEREVENT

        for i in range(64):
            if obs[i]==0:
                steeeps+=1
        
        ido,ans= self.dfs_find(obs,sc,0,4,[],move_list,areas_list,steep_list,steeeps, good_move, bad_move)
        anss = ans[0]

        return (self.col_offset + (anss%8) * self.block_len, self.row_offset + (anss//8) * self.block_len), pygame.USEREVENT

    def dfs_find(self,obs,sc,time,n,step,move_list,areas_list,steep_list,steeeps, good_move, bad_move):
        color_now = 1
        if self.color == 'black':
            color_now = -1
        if time==n:
            area = []
            if steeeps>15:
                for i in range(64):
                    can = self.can_place(obs,i,sc)
                    if can:
                        area.append(i)
                return len(area),step.copy()
            else:
                area = self.how_many(obs,color_now)
                return area , step.copy()
            
        areas,steeps,move = [],[],[]

        for i in range(64):
            if color_now == sc:
                can = self.can_place(obs,i,sc)
                if can and i in good_move:
                    move.append(i)
            else:
                can = self.can_place(obs,i,sc)
                if can:
                    move.append(i)
        if move == []:
            for i in range(64):
                can = self.can_place(obs,i,sc)
                if can and i not in bad_move:
                     move.append(i)
        if move == []:
            for i in range(64):
                can = self.can_place(obs,i,sc)
                if can:
                     move.append(i)
        move_list.append(move)

        if sc == color_now and move==[]:
            return -1,step.copy()
        elif sc == color_now*(-1) and move==[] :
            return 100,step.copy()
        
        for i in move_list[-1]:
            k = self.flip_or_not(i%8,i//8,obs,sc)
            step.append(i)
            area,steep = self.dfs_find(k,sc*(-1),time+1,n,step,move_list,areas_list,steep_list,steeeps, good_move, bad_move)
            step.pop(-1)
            areas.append(area)
            steeps.append(steep)

        if sc == color_now :
            smallest_area = min(areas)
        else :
            smallest_area = max(areas)
        n=0
        ns = []
        for i in areas:
            if i == smallest_area:
                ns.append(n)
            n+=1
        
        return smallest_area,steeps[random.randint(0,len(ns)-1)]

class MyAgent_0(MyAgent):
    def step(self,reward,obs):
        move = []
        sc = 1
        if self.color == 'black': 
            sc = -1
        for i in [0,7,63,56]:
            can = self.can_place(obs,i,sc)
            if can:
                move.append(i)
        if move!=[]:
            anss = move[random.randint(0,len(move)-1)]
            return (self.col_offset + (anss%8) * self.block_len, self.row_offset + (anss//8) * self.block_len), pygame.USEREVENT
        move = []
        for i in range(64):
            can = self.can_place(obs,i,sc)
            if can :
                move.append(i)
        p = random.randint(0,len(move)-1)
        return (self.col_offset + (move[p]%8) * self.block_len, self.row_offset + (move[p]//8) * self.block_len), pygame.USEREVENT
            

class MyAgent_knaw(MyAgent):
    def step(self, reward, obs):
        move_list,areas_list,steep_list = [],[],[]
        sc = 1
        if self.color == 'black': 
            sc = -1
 
        steeeps = 0
        for i in range(64):
            if obs[i]==0:
                steeeps+=1
        
        ido,ans,hhh= self.dfs_find(obs,sc,0,2,[],move_list,areas_list,steep_list,steeeps,)
        ido+=1
        hhh+=1
        anss = ans[0]
 
        return (self.col_offset + (anss%8) * self.block_len, self.row_offset + (anss//8) * self.block_len), pygame.USEREVENT
 
    def dfs_find(self,obs,sc,time,n,step,move_list,areas_list,steep_list,steeeps,):
        color_now = 1
        if self.color == 'black':
            color_now = -1
        if time==n:
            area = []
            if steeeps>15:
                for i in range(64):
                    can = self.can_place(obs,i,sc)
                    if can:
                        area.append(i)
                    heavy = self.how_heavy(obs,sc,color_now,step[0])
                return len(area) ,step.copy(),heavy
            else:
                area = self.how_many(obs,-1)
                heavy = self.how_heavy(obs,sc,color_now,step[0])
                return area, step.copy() ,heavy
            
        areas,steeps,move,heavys = [],[],[],[]
 
        for i in range(64):
                can = self.can_place(obs,i,sc)
                if can :
                    move.append(i)
 
        move_list.append(move)
 
        if sc == color_now and move==[]:
            heavy = self.how_heavy(obs,sc,color_now,step[0])
            return -1,step.copy(),heavy
        elif sc == color_now*(-1) and move==[] :
            heavy = self.how_heavy(obs,sc,color_now,step[0])
            return 100,step.copy(),heavy
        
        for i in move_list[-1]:
            k = self.flip_or_not(i%8,i//8,obs,sc)
            step.append(i)
            area, steep, heavy = self.dfs_find(k,sc*(-1),time+1,n,step,move_list,areas_list,steep_list,steeeps, )
            step.pop(-1)
            areas.append(area)
            heavys.append(heavy)
            steeps.append(steep)
 
        n,t=0,0
        ts = []
        for i in heavys:
            if i == max(heavys):
                ts.append(t)
            t+=1
        maxi=ts[0]
        maxii=areas[0]
        if len(ts)>1:
            if sc == color_now :
                for i in ts:
                    if areas[i] < maxii:
                        maxi = i 
                        maxii = areas[i]
                    if areas[i]==maxii and random.randint(0,1)==1:
                        maxi = i
            else :
                for i in ts:
                    if areas[i] > maxii:
                        maxi = i
                        maxii = areas[i]
                    if areas[i]==maxii and random.randint(0,1)==1:
                        maxi = i
        return areas[maxi],steeps[maxi],heavys[maxi]
 
    def how_heavy(self,obs,sc,color_now,place):
        weight=[
            200,-200,100,100,100,100,-200,200,
            -200,-200,1,1,1,1,-200,-200,
            100,1,1,1,1,1,1,100,
            100,1,1,1,1,1,1,100,
            100,1,1,1,1,1,1,100,
            100,1,1,1,1,1,1,100,
            -200,-200,1,1,1,1,-200,-200,
            200,-200,100,100,100,100,-200,200,
        ]
        if obs[0]==color_now:
            weight[1]=200
            weight[8]=200
        if obs[7]==color_now:
            weight[6]=200
            weight[15]=200
        if obs[56]==color_now:
            weight[57]=200
            weight[46]=200
        if obs[63]==color_now:
            weight[62]=200
            weight[55]=200
 
        return weight[place]


if __name__ == "__main__":
    agent = RandomAgent()
    print(agent.step(None, None))