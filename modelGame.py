from mod import basic_shapes as bs, easy_shaders as es, scene_graph as sg, transformations as tr
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import glClearColor
import random

def grid(N, edge = 0.1):
    """
    Se calculan los puntos de la grilla (centro de cada cuadrado)
    """
    lado = (2 - edge)/N
    start = edge + lado/2 - 1
    end = 1 - edge - lado/2
    axis = np.linspace(start, end, N)
    return [lado, axis]

def enArco(v1, v2, punto):
    """
    Indica si punto está en el segmento que une v1 y v2
    """
    if v1[1] == v2[1]:
        if punto[1] != v2[1]:
            return False
        elif v2[0] > v1[0]:
            return v1[0] <= punto[0] <= v2[0]
        else:
            return v2[0] <= punto[0] <= v1[0]
    else:
        if punto[0] != v2[0]:
            return False
        elif v2[1] > v1[1]:
            return v1[1] <= punto[1] <= v2[1]
        else:
            return v2[1] <= punto[1] <= v1[1]

def enTrayecto(listaPares, punto):
    """
    Indica si punto se encuentra en el camino definido por los puntos de listaPares
    """
    n = len(listaPares)
    for i in range(n-1):
        if enArco(listaPares[i], listaPares[i + 1], punto):
            return True
    return False

def masCercano(number, arreglo):
    """
    Entrega el valor y posición del elemento de arreglo más cercano a number
    """
    array = np.abs(arreglo-number)
    valor = np.amin(array)
    index = np.where(array == valor)[0][0]
    valor = arreglo[index]
    return [valor, index]

def posInGrid(x,y,grilla):
    """
    Entrega la posición de la celda en la que se encuentra el punto x,y; según grilla
    """
    horizontal = masCercano(x,grilla)
    vertical = masCercano(y, grilla)
    return [horizontal[0],vertical[0]]

def largoDosPuntos(p1, p2):
    """
    Entrega la distancia entre 2 puntos, cuando estos tienen al menos una coordenada igual
    """
    return np.abs(np.sum(np.array(p2)-np.array(p1)))

def largo(posAd, posAt, nodos=None):
    """
    Entrega la distancia entre los puntos posAd y posAt, dada por el camino definido por nodos
    """
    if nodos is None:
        nodos = []
    n = len(nodos)
    if not n:
        return largoDosPuntos(posAd,posAt)
    else:
        large = largoDosPuntos(posAd,nodos[0])+largoDosPuntos(posAt,nodos[-1])
        for i in range(n-1):
            large += largoDosPuntos(nodos[i],nodos[i+1])
        return large


class Square:

    # Crea un cuadrado con textura

    def __init__(self,N):
        self.lado = grid(N)[0]

    def getElementoCuerpo(self, imagen):
        gpuSquare = es.toGPUShape(bs.createTextureQuad(imagen), GL_REPEAT, GL_NEAREST)

        body = sg.SceneGraphNode('body')
        body.transform = tr.matmul((tr.scale(self.lado, self.lado, 1), tr.rotationZ(-np.pi/2)))
        body.childs += [gpuSquare]
        return body

class Edge:

    # Se crea el borde del mapa

    def __init__(self,N, edge = 0.1):

        self.lado, self.grilla = grid(N)

        gpuBorde = es.toGPUShape(bs.createColorQuad(0, 0, 0))

        bord = sg.SceneGraphNode('borde')
        bord.transform = tr.scale(edge, 2, 1)
        bord.childs += [gpuBorde]

        bordeIzq = sg.SceneGraphNode('bordeIzq')
        bordeIzq.transform = tr.translate(-1+edge/2,0,0)
        bordeIzq.childs += [bord]

        bordeDer = sg.SceneGraphNode('bordeDer')
        bordeDer.transform = tr.translate(1 - edge / 2, 0, 0)
        bordeDer.childs += [bord]

        bordeSup = sg.SceneGraphNode('bordeSup')
        bordeSup.transform = tr.matmul([tr.translate(0,1-edge/2,0),tr.rotationZ(np.pi/2)])
        bordeSup.childs += [bord]

        bordeInf = sg.SceneGraphNode('bordeInf')
        bordeInf.transform = tr.matmul([tr.translate(0, -1 + edge / 2, 0), tr.rotationZ(np.pi/2)])
        bordeInf.childs += [bord]

        bordeMapa = sg.SceneGraphNode('bordeMapa')
        bordeMapa.childs = [bordeIzq, bordeDer, bordeSup, bordeInf]

        self.model = bordeMapa

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

class Cells:

    # Se crea el mapa cuadriculado

    def __init__(self, imagen, N, edge = 0.1):
        self.lado = grid(N)[0]

        gpuSquare = es.toGPUShape(bs.createTextureQuad(imagen, N/2, N/2), GL_REPEAT, GL_NEAREST)

        mapa = sg.SceneGraphNode('mapa')
        mapa.transform = tr.uniformScale(2-2*edge)
        mapa.childs += [gpuSquare]
        self.model = mapa

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

class GameOver:

    # Se crea la escena desplegada cuando el jugador pierde

    def __init__(self, goImage, blood, N):
        self.lado = grid(N)[0]
        gpuGameOver = es.toGPUShape(bs.createTextureQuad(goImage), GL_REPEAT, GL_NEAREST)
        gpuBlood = es.toGPUShape(bs.createTextureQuad(blood), GL_REPEAT, GL_NEAREST)

        go = sg.SceneGraphNode('go')
        go.childs += [gpuGameOver]
        self.pos = [0,0]

        blood = sg.SceneGraphNode('blood')
        blood.childs += [gpuBlood]

        escenaFinal = sg.SceneGraphNode('final')
        escenaFinal.childs += [go, blood]

        self.theta = 0
        self.size = 1
        self.muerto = False
        self.crece = True
        self.gira = True
        self.model = escenaFinal

    def update(self, dt):
        if self.muerto:
            if self.crece and self.gira:
                if self.size*0.1 >= 1.8 and np.abs(np.cos(self.theta)-1) <= 0.02 and np.abs(np.sin(self.theta)) <= 0.02:
                    self.crece = False
                    self.gira = False
                    self.theta = 0
                else:
                    self.theta += 3000*dt/(self.size**2.6)
                    self.size += 3*dt/(self.size**0.15)
        else:
            return

    def draw(self, pipeline):
        if self.muerto:
            glUseProgram(pipeline.shaderProgram)
            gameOverMove = sg.findNode(self.model, 'go')
            gameOverMove.transform = tr.matmul([tr.uniformScale(self.size*0.1),tr.rotationZ(self.theta), tr.translate(-0.015, 0, 0)])
            bloodPos = sg.findNode(self.model, 'blood')
            bloodPos.transform = tr.matmul((tr.translate(self.pos[0], self.pos[1], 0), tr.uniformScale(self.lado*3)))
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
            self.model.transform = tr.identity()
            sg.drawSceneGraphNode(self.model, pipeline, 'transform')

class Apple:

    # Se crea el modelo de manzana

    def __init__(self,N):
        self.lado = grid(N)[0]

        gpuCircle = es.toGPUShape(bs.createColorCircle(0.8, 0.05, 0.05))

        circulo = sg.SceneGraphNode('circulo')
        circulo.transform = tr.uniformScale(self.lado)
        circulo.childs += [gpuCircle]

        gpuLuz = es.toGPUShape(bs.createColorCircle(0.9, 0.7, 0.7))
        luz = sg.SceneGraphNode('luz')
        luz.transform = tr.matmul([tr.translate(-self.lado/5,self.lado/5,0),tr.uniformScale(self.lado/3)])
        luz.childs += [gpuLuz]

        gpuTallo = es.toGPUShape(bs.createColorQuad(120/255, 69/255, 19/255))
        tallo = sg.SceneGraphNode('tallo')
        tallo.transform = tr.matmul([tr.translate(0, self.lado/2 , 0), tr.scale(self.lado / 10, self.lado / 3, 1)])
        tallo.childs += [gpuTallo]

        gpuHoja = es.toGPUShape(bs.createColorCircle(50 / 255, 205 / 255, 50 / 255))
        hoja = sg.SceneGraphNode('hoja')
        sx = 5
        sy = 2
        hoja.transform = tr.matmul([tr.translate((self.lado / sx) * np.cos(np.pi / 3) + 0.006, self.lado / 2 +
                                                 self.lado / (2 * sy) * np.sin(np.pi / 3) + 0.005, 0),
                                    tr.rotationZ(-np.pi/3), tr.scale(self.lado / sx, self.lado / sy, 1)])
        hoja.childs += [gpuHoja]

        redManzana = sg.SceneGraphNode('redManzana')
        redManzana.childs += [circulo, luz, tallo, hoja]
        self.model = redManzana

class AppleCreator:

    # Se crea el objeto que se encarga de dibujar las manzanas en lugares donde no esté la serpiente

    def __init__(self,N,n):
        self.lado, self.grilla = grid(N)
        self.n = n
        self.N = N
        paresSnake = []
        for i in range(self.n+1):
            par = [self.grilla[(N + N % 2) // 2+i], self.grilla[(N + N % 2) // 2]]
            paresSnake.append(par)
        while True:
            a = random.choice(self.grilla)
            b = random.choice(self.grilla)
            pos = [a, b]
            # Si la posición escogida al azar no está ocupada por la serpiente, se detiene el loop
            if pos not in paresSnake:
                self.pos = pos
                break
        self.model = Apple(N).model
        self.posSnake = None

    def verticesSerpiente(self,cola):
        vertices = [posInGrid(cola.pos_x, cola.pos_y, self.grilla)]
        parametro = cola.lead
        while not isinstance(parametro,Head):
            n = len(parametro.giro)
            if n > 0:
                for i in range(n//4):
                    par = [parametro.giro[i*4], parametro.giro[i*4+1]]
                    if par not in vertices:
                        vertices.append(par)
            parametro = parametro.lead
        posHead = posInGrid(parametro.pos_x, parametro.pos_y, self.grilla)
        vertices.append(posHead)
        self.posSnake = vertices

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        self.model.transform = tr.translate(self.pos[0], self.pos[1], 0)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def createNew(self):
        while True:
            a = random.choice(self.grilla)
            b = random.choice(self.grilla)
            pos = [a, b]
            if not enTrayecto(self.posSnake, pos):
                self.pos = pos
                break

class BodyPart:

    theta = 0
    direccion = 'left'
    giro = []
    estado = True

    def __init__(self, N, imagen, edge = 0.1):
        self.lado, self.grilla = grid(N)
        self.N = N
        partMoving = sg.SceneGraphNode('part')
        partMoving.childs += [Square(N).getElementoCuerpo(imagen)]
        self.model = partMoving
        self.pos_x = self.grilla[(N + N % 2) // 2]
        self.pos_y = self.grilla[(N + N % 2) // 2]
        self.edge = edge

    def update(self, dt):
        if self.estado:
            self.nextPos(dt)

    def nextPos(self, dt):
        if self.direccion == 'right':
            self.pos_x = self.pos_x + dt

        elif self.direccion == 'left':
            self.pos_x = self.pos_x - dt

        elif self.direccion == 'up':
            self.pos_y = self.pos_y + dt

        else:
            self.pos_y = self.pos_y - dt

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos_x, self.pos_y,0),tr.rotationZ(self.theta)])
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

class Head(BodyPart):

    celdasSnake = None
    giroPropio = None

    def __init__(self, N, imagen, edge = 0.1):
        super().__init__(N, imagen, edge)

    def direction(self, r, theta1, vertice_x, vertice_y):
        if self.estado:
            self.direccion = r
            self.theta += theta1
            self.pos_x = vertice_x
            self.pos_y = vertice_y
            self.giro += [self.pos_x,self.pos_y, r, theta1]

    def updatePart(self, parts):
        vertices = []
        vertices += [posInGrid((parts[-1]).pos_x, (parts[-1]).pos_y, self.grilla)]
        nPartes = len(parts)
        for i in range(nPartes - 2):
            n = len(parts[-(i + 2)].giroPropio)
            for j in range(n // 4):
                par = [parts[-(i + 2)].giroPropio[j * 4], parts[-(i + 2)].giroPropio[j * 4 + 1]]
                if par not in vertices:
                    vertices.append(par)
        self.celdasSnake = vertices

    def comer(self, manzana, cuerpo, n, imagen):
        if self.estado:
            if posInGrid(self.pos_x, self.pos_y, self.grilla) == manzana.pos:
                manzana.verticesSerpiente(cuerpo[n-1])
                manzana.createNew()
                cuerpo[-1].tieneSeguidor()
                cuerpo.append(TailGrow(cuerpo[-1], self.N, imagen))
                n += 1
                return n, cuerpo
            else:
                return n, cuerpo
        else:
            return n, cuerpo

    def choque(self, seAcabo):
        if not self.estado:
            return
        maxim = 1 - self.edge
        minim = self.edge - 1
        posActual = posInGrid(self.pos_x,self.pos_y, self.grilla)
        if not minim <= self.pos_y <= maxim or not minim <= self.pos_x <= maxim:
            self.estado = False
            glClearColor(0.3, 0.3, 0.3, 1.0)
            seAcabo.pos = [self.pos_x, self.pos_y]
            seAcabo.muerto = True
        if enTrayecto(self.celdasSnake, posActual):
            self.estado = False
            glClearColor(0.3, 0.3, 0.3, 1.0)
            seAcabo.pos = [self.pos_x, self.pos_y]
            seAcabo.muerto = True

class MiddlePart(BodyPart):

    def __init__(self, sucesor, N, imagen, edge = 0.1):
        super().__init__(N, imagen, edge)
        self.lead = sucesor
        self.giro = self.lead.giroPropio
        self.giroPropio = []
        self.estado = self.lead.estado

        if self.lead.direccion == 'left':
            self.pos_x = self.lead.pos_x + self.lead.lado
            self.pos_y = self.lead.pos_y

        elif self.lead.direccion == 'right':
            self.pos_x = self.lead.pos_x - self.lead.lado
            self.pos_y = self.lead.pos_y

        elif self.lead.direccion == 'up':
            self.pos_x = self.lead.pos_x
            self.pos_y = self.lead.pos_y - self.lead.lado

        elif self.lead.direccion == 'down':
            self.pos_x = self.lead.pos_x
            self.pos_y = self.lead.pos_y + self.lead.lado

        self.theta = self.lead.theta
        self.direccion = self.lead.direccion

    def turnH(self, parteGiro):
        self.direccion = parteGiro[2]
        self.theta += parteGiro[3]
        self.pos_y = parteGiro[1]
        if parteGiro[2] == 'right':
            self.pos_x = self.lead.pos_x - self.lado
        else:
            self.pos_x = self.lead.pos_x + self.lado
        self.giroPropio += parteGiro
        del self.giro[0:4]

    def turnV(self, parteGiro):
        self.direccion = parteGiro[2]
        self.theta += parteGiro[3]
        self.giroPropio += parteGiro
        if parteGiro[2] == 'up':
            self.pos_y = self.lead.pos_y - self.lado
        else:
            self.pos_y = self.lead.pos_y + self.lado
        self.pos_x = parteGiro[0]
        del self.giro[0:4]

    def change(self):
        parteGiro = self.giro[0:4]
        if self.direccion == 'up':
            if self.pos_y >= parteGiro[1]:
                self.turnH(parteGiro)

        elif self.direccion == 'down':
            if self.pos_y <= parteGiro[1]:
                self.turnH(parteGiro)

        elif self.direccion == 'left':
            if self.pos_x <= parteGiro[0]:
                self.turnV(parteGiro)

        elif self.direccion == 'right':
            if self.pos_x >= parteGiro[0]:
                self.turnV(parteGiro)
        else:
            return

    def updateDirection(self):
        if not self.lead.estado:
            self.estado = False
            return
        if len(self.giro) > 0:
            self.change()

class Neck(MiddlePart):

    def __init__(self, sucesor, N, imagen, edge = 0.1):
        super().__init__(sucesor, N, imagen, edge)
        self.giro = self.lead.giro

class Tail(MiddlePart):

    def __init__(self, sucesor, N, imagen, edge = 0.1):
        super().__init__(sucesor, N, imagen, edge)
        self.seguidor = False

    def updateDirection(self):
        if not self.lead.estado:
            self.estado = False
            return
        if len(self.giro) > 0:
            self.change()

    def turnH(self, parteGiro):
        self.direccion = parteGiro[2]
        self.theta += parteGiro[3]

        if parteGiro[2] == 'right':
            self.pos_x = self.lead.pos_x - self.lado
        else:
            self.pos_x = self.lead.pos_x + self.lado

        self.pos_y = parteGiro[1]

        if self.seguidor:
            self.giroPropio += parteGiro
        del self.giro[0:4]

    def turnV(self, parteGiro):
        self.direccion = parteGiro[2]
        self.theta += parteGiro[3]

        if parteGiro[2] == 'up':
            self.pos_y = self.lead.pos_y - self.lado
        else:
            self.pos_y = self.lead.pos_y + self.lado

        if self.seguidor:
            self.giroPropio += parteGiro
        self.pos_x = parteGiro[0]
        del self.giro[0:4]

    def tieneSeguidor(self):
        self.seguidor = True

class TailGrow(Tail):

    def __init__(self, sucesor, N, imagen, edge = 0.1):
        super().__init__(sucesor, N, imagen, edge)
        self.pos_x = sucesor.pos_x
        self.pos_y = sucesor.pos_y
        self.direccion = self.lead.direccion
        self.moverse = False
        self.theta = sucesor.theta

    def still(self):
        nNodos = len(self.giro)
        if nNodos > 0:
            nodos = []
            for i in range(nNodos // 4):
                nodo = [self.giro[i * 4], self.giro[i * 4 + 1]]
                nodos.append(nodo)
            if largo([self.lead.pos_x, self.lead.pos_y], [self.pos_x, self.pos_y], nodos) >= self.lado:
                self.moverse = True
        else:
            if largo([self.lead.pos_x, self.lead.pos_y], [self.pos_x, self.pos_y]) >= self.lado:
                self.moverse = True

    def updateDirection(self):
        if not self.lead.estado:
            self.estado = False
            return
        if not self.moverse:
            self.still()
        else:
            if len(self.giro) > 0:
                self.change()

    def update(self, dt):
        if self.moverse and self.estado:
            self.nextPos(dt)