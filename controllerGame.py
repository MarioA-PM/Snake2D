import glfw
import sys
import numpy as np
from modelGame import masCercano

def deltaTiempo(tiempos):
    dt = []
    n = len(tiempos)
    for i in range(n-1):
        dt.append(tiempos[i+1]-tiempos[i])
    return max(dt)


class Controller:

    def __init__(self):
        self.model = None
        self.ajuste = False
        self.tiempoCambio = [-100000, -50000, -10000, -7500, -5000, -3000, 0]
        self.factor = 0

    def set_model(self, m, N, velocidad):
        self.model = m
        if velocidad == 'normal':
            self.factor = 0.3
        else:
            f10 = 0.22
            f15 = 0.2
            self.factor = (N - 10) * ((f15 - f10) / 5) + f10
            del self.tiempoCambio[-4:]

        if 10 <= N < 14 and velocidad == 'normal':
            self.ajuste = True
        elif N >= 15 and velocidad == 'normal':
            self.ajuste = False
        elif velocidad == 'BAJA' and N<=15:
            self.ajuste = True
        else:
            self.ajuste = False

    def timeHL(self, vertice_x, vertice_y):
        ti = glfw.get_time()
        del self.tiempoCambio[0]
        self.tiempoCambio.append(ti)

        if self.model.direccion == 'up':
            self.model.direction('left', np.pi / 2, vertice_x, vertice_y)
        else:
            self.model.direction('left', -np.pi / 2, vertice_x, vertice_y)

    def timeHR(self, vertice_x, vertice_y):
        ti = glfw.get_time()
        del self.tiempoCambio[0]
        self.tiempoCambio.append(ti)

        if self.model.direccion == 'up':
            self.model.direction('right', -np.pi / 2, vertice_x, vertice_y)
        else:
            self.model.direction('right', np.pi / 2, vertice_x, vertice_y)

    def timeVU(self, vertice_x, vertice_y):
        ti = glfw.get_time()
        del self.tiempoCambio[0]
        self.tiempoCambio.append(ti)

        if self.model.direccion == 'left':
            self.model.direction('up', -np.pi / 2, vertice_x, vertice_y)
        else:
            self.model.direction('up', np.pi / 2, vertice_x, vertice_y)

    def timeVD(self, vertice_x, vertice_y):
        ti = glfw.get_time()
        del self.tiempoCambio[0]
        self.tiempoCambio.append(ti)

        if self.model.direccion == 'left':
            self.model.direction('down', np.pi / 2, vertice_x, vertice_y)
        else:
            self.model.direction('down', -np.pi / 2, vertice_x, vertice_y)


    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()
        vertice_x = masCercano(self.model.pos_x, self.model.grilla)[0]
        vertice_y = masCercano(self.model.pos_y, self.model.grilla)[0]

        if self.ajuste:
            n = len(self.model.giro)
            tiempoPromedio = deltaTiempo(self.tiempoCambio)
            if n > 0:
                if key == glfw.KEY_LEFT and vertice_y != self.model.giro[-3] and\
                        self.model.direccion != 'left' and\
                        self.model.direccion != 'right' and\
                        tiempoPromedio >= self.factor:
                    self.timeHL(vertice_x, vertice_y)

                elif key == glfw.KEY_RIGHT and vertice_y != self.model.giro[-3] and\
                        self.model.direccion != 'left' and\
                        self.model.direccion != 'right' and\
                        tiempoPromedio >= self.factor:
                    self.timeHR(vertice_x, vertice_y)


                elif key == glfw.KEY_UP and vertice_x != self.model.giro[-4] and\
                        self.model.direccion != 'up' and\
                        self.model.direccion != 'down' and\
                        tiempoPromedio >= self.factor:

                    self.timeVU(vertice_x, vertice_y)

                elif key == glfw.KEY_DOWN and vertice_x != self.model.giro[-4] and\
                        self.model.direccion != 'up' and\
                        self.model.direccion != 'down' and\
                        tiempoPromedio >= self.factor:

                    self.timeVD(vertice_x, vertice_y)

            else:
                if key == glfw.KEY_LEFT and self.model.direccion != 'left' and self.model.direccion != 'right':

                    self.timeHL(vertice_x, vertice_y)


                elif key == glfw.KEY_RIGHT and self.model.direccion != 'left' and self.model.direccion != 'right':

                    self.timeHR(vertice_x, vertice_y)


                elif key == glfw.KEY_UP and self.model.direccion != 'up' and self.model.direccion != 'down':

                    self.timeVU(vertice_x, vertice_y)

                elif key == glfw.KEY_DOWN and self.model.direccion != 'up' and self.model.direccion != 'down':

                    self.timeVD(vertice_x, vertice_y)

        else:
            if len(self.model.giro) > 0:
                if key == glfw.KEY_LEFT and vertice_y != self.model.giro[
                    -3] and self.model.direccion != 'left' and self.model.direccion != 'right':
                    if self.model.direccion == 'up':
                        self.model.direction('left', np.pi / 2, vertice_x, vertice_y)
                    else:
                        self.model.direction('left', -np.pi / 2, vertice_x, vertice_y)

                elif key == glfw.KEY_RIGHT and vertice_y != self.model.giro[
                    -3] and self.model.direccion != 'left' and self.model.direccion != 'right':
                    if self.model.direccion == 'up':
                        self.model.direction('right', -np.pi / 2, vertice_x, vertice_y)
                    else:
                        self.model.direction('right', np.pi / 2, vertice_x, vertice_y)


                elif key == glfw.KEY_UP and vertice_x != self.model.giro[
                    -4] and self.model.direccion != 'up' and self.model.direccion != 'down':
                    if self.model.direccion == 'left':
                        self.model.direction('up', -np.pi / 2, vertice_x, vertice_y)
                    else:
                        self.model.direction('up', np.pi / 2, vertice_x, vertice_y)

                elif key == glfw.KEY_DOWN and vertice_x != self.model.giro[
                    -4] and self.model.direccion != 'up' and self.model.direccion != 'down':
                    if self.model.direccion == 'left':
                        self.model.direction('down', np.pi / 2, vertice_x, vertice_y)
                    else:
                        self.model.direction('down', -np.pi / 2, vertice_x, vertice_y)

            else:
                if key == glfw.KEY_LEFT and self.model.direccion != 'left' and self.model.direccion !='right':
                    if self.model.direccion == 'up':
                        self.model.direction('left', np.pi/2, vertice_x, vertice_y)
                    else:
                        self.model.direction('left', -np.pi/2, vertice_x, vertice_y)


                elif key == glfw.KEY_RIGHT and self.model.direccion != 'left' and self.model.direccion != 'right':
                    if self.model.direccion == 'up':
                        self.model.direction('right', -np.pi/2, vertice_x, vertice_y)
                    else:
                        self.model.direction('right', np.pi/2, vertice_x, vertice_y)


                elif key == glfw.KEY_UP and self.model.direccion != 'up' and self.model.direccion != 'down':
                    if self.model.direccion == 'left':
                        self.model.direction('up', -np.pi/2, vertice_x, vertice_y)
                    else:
                        self.model.direction('up', np.pi/2, vertice_x, vertice_y)

                elif key == glfw.KEY_DOWN and self.model.direccion != 'up' and self.model.direccion != 'down':
                    if self.model.direccion == 'left':
                        self.model.direction('down', np.pi/2, vertice_x, vertice_y)
                    else:
                        self.model.direction('down', -np.pi/2, vertice_x, vertice_y)
