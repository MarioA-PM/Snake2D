import glfw
import sys
from modelGame import *
from controllerGame import Controller
import random

if __name__ == "__main__":

    # Recibe los argumentos de entrada
    if len(sys.argv) <= 1 or len(sys.argv) > 3:
        raise Exception('No se ingresó el tamaño del mapa')
    elif not 10 <= int(sys.argv[1]) <= 50:
        raise Exception('El tamaño ingresado no está permitido')
    else:
        if len(sys.argv) == 2:
            N = int(sys.argv[1])
            f10 = 1.5
            f50 = 1/1.6
            f = (N-10)*((f50-f10)/40)+f10
            velocidad = 'normal'
        else:
            velocidad = (sys.argv[2]).upper()
            if velocidad == 'BAJA':
                N = int(sys.argv[1])
                f10 = 0.8
                f50 = 1 / 1.8
                f = (N - 10) * ((f50 - f10) / 40) + f10
            else:
                velocidad = 'normal'
                N = int(sys.argv[1])
                f10 = 1.5
                f50 = 1 / 1.6
                f = (N - 10) * ((f50 - f10) / 40) + f10

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Super Snake 3000", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    glfw.set_key_callback(window, controlador.on_key)

    pipeline = es.SimpleTransformShaderProgram()
    pipeline_texture = es.SimpleTextureTransformShaderProgram()

    glClearColor(0.4, 0.4, 0.8, 1.0)

    # Lista con el nombre de figuras a utilizar
    figuras = ['resources/fig/mushroom.png', 'resources/fig/head.png', 'resources/fig/boo.png',
               'resources/fig/snakeHead.png']
    
    # Se habilitan las transparencias
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Se crean los objetos
    snake = Head(N,'resources/fig/snakeHead.png') # Cabeza de la serpiente
    parte1 = Neck(snake, N,random.choice(figuras))

    # Se almacenan todas las partes de la serpiente, menos la cabeza
    partes = [parte1]

    # Objetos correspondientes al borde, la grilla y la escena final
    borde = Edge(N)
    juegoTerminado = GameOver('resources/fig/go.png', 'resources/fig/blood.png', N)
    grilla = Cells('resources/fig/tableroDark.png', N)

    # Se crean las siguientes partes de la serpiente
    n = 4

    for i in range(n-2):
        partBody = MiddlePart(partes[i],N,random.choice(figuras))
        partes.append(partBody)

    controlador.set_model(snake, N, velocidad)
    partes.append(Tail(partes[-1],N,random.choice(figuras)))

    # Objeto que crea las manzanas
    manzana = AppleCreator(N, n)

    t0 = 0
    tiempo_1 = glfw.get_time()

    while not glfw.window_should_close(window):

        # Se calcula la diferencia de tiempo entre cada ejecución del ciclo
        ti = glfw.get_time()
        moverse = (ti - tiempo_1 >= 2) # Retrasa en 2 s el movimiento de la serpiente al ejecutarse el programa
        dift = (ti-t0)*moverse
        t0 = ti
        glfw.poll_events()
        dt = dift*f

        glClear(GL_COLOR_BUFFER_BIT)

        # Se dibuja la grilla y el borde
        grilla.draw(pipeline_texture)
        borde.draw(pipeline)

        # Se actualizan los objetos
        snake.update(dt)
        snake.updatePart(partes)
        for i in range(n):
            partes[i].updateDirection()
        for i in range(n):
            partes[i].update(dt)

        # Se comprueba si se come una manzana
        n, partes = snake.comer(manzana, partes, n, random.choice(figuras))

        # Se verifica si la serpiente choca
        snake.choque(juegoTerminado)

        # Se dibuja la serpiente
        for i in range(n):
            partes[i].draw(pipeline_texture)
        snake.draw(pipeline_texture)

        # Se dibuja la manzana
        manzana.draw(pipeline)

        # Se actualiza y dibuja la escena final en caso de terminar el juego
        juegoTerminado.update(2.2*dift)
        juegoTerminado.draw(pipeline_texture)

        glfw.swap_buffers(window)

    glfw.terminate()
