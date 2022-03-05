from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
import random


N = 100
NPROD = 5
NCONS = 1

'''
Tenemos una lista de semáforos (sems) de 2 en 2
el primero (sems[2*ide]) es el semaforo empty del productor ide
el segundo (sems[2*ide +1]) es el semaforo nonEmpty del productor ide
'''

def productor(ide, buffer, sems):
    prod = 0
    for v in range(N):
        prod += random.randint(0,5)
        print (f"productor nº{ide} produciendo {prod} en bucle {v}")        
        sems[2*ide].acquire()       # wait empty
        buffer[ide]= prod
        print('Estado del buffer: ' +str(list(buffer)))
        sems[2*ide +1].release()  #signal nonempty
        print (f"productor nº{ide} ha almacenado {prod}")
    prod = -1
    print (f"productor nº{ide} produciendo {prod}")        
    sems[2*ide].acquire()       #wait empty
    buffer[ide]= prod
    sems[2*ide +1].release()    #signal nonEmpty
    print (f"productor nº{ide} ha almacenado {prod}")
    
    
def no_num(n,num=-1):
    return n != num

def min_buffer(lista):         
    mod =  list(filter(no_num, lista))  #Obviamos los -1 de la lista
    if mod != []:
        minim= min(mod)
        for i in range(len(lista)):     #recuperamos la posición del mínimo
            if lista[i] == minim:
                index = i
                return minim,index
    else:
        return -1,-1
        
        
        
def consumidor (buffer,sems):
    minim = 0               #inicialización del bucle while
    salida = []
    for i in range(NPROD):
        sems[2*i + 1].acquire()     #Nos aseguramos que todos han generado
        #print (f"consumidor revisado nº {i}")
    (minim, ide) = min_buffer(buffer)   
    while minim != -1:
        
        print (f"consumidor desalmacenando estantería nº {ide}")
        salida.append(minim)
        
        sems[2*ide].release()   #signal empty
        print (f"consumidor consumiendo {minim}")
        sems[2*ide + 1].acquire()  #wait nonEmpty
        (minim, ide) = min_buffer(buffer)
        
    print(salida)
    print(len(salida))
    return salida


def main():
    buffer = Array('i', NPROD) #ALmacen de los productos (1 de capacidad por productor)

    sems = []
    for i in range(NPROD): #Generamos la lista de semáforos
        non_empty = Semaphore(0)
        empty = BoundedSemaphore(1)
        sems.append(empty)
        sems.append(non_empty)
    
#GENERAMOS LOS PROCESOS DE PRODUCTORES
    prodlst = [ Process(target=productor,
                        name=f'prod_{i}',
                        args=(i, buffer, sems))
                for i in range(NPROD) ]
#GENERAMOS EL PROCESO DE CONSUMIDOR
    cons=  Process(target=consumidor, args=(buffer, sems))
#INICNIAMOS LOS PROCESOS
    for p in prodlst:
        p.start()
    cons.start()

    for p in prodlst:
        p.join()
    cons.join()

if __name__ == '__main__':
    main()
