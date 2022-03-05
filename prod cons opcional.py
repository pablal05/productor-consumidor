#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 10:20:05 2022

@author: mat
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
import random


N = 100
n = 3
NPROD = 3
NCONS = 1

'''
Tenemos una lista de semáforos (sems) de 3 en 3
el primero (sems[3*ide]) es el semaforo empty del productor ide
el segundo (sems[3*ide +1]) es el semaforo nonEmpty del productor ide
el tercero (sems[3*ide + 2]) es el semaforo mutex (Lock()) del productor ide
'''

def productor(ide, buffer, sems, index):
    prod = 0
    for v in range(N):
        prod += random.randint(0,5)
        print (f"productor nº{ide} produciendo {prod} en bucle {v}")        
        sems[3*ide].acquire()   #wait empty 
            
        add_data(ide,buffer, sems, index, prod)
        sems[3*ide +1].release()    #signal non empty
        print (f"productor nº{ide} ha almacenado {prod}, tiene {index[ide]} productos")

        
        
    prod = -1
    print (f"productor nº{ide} produciendo {prod}")        
    sems[3*ide].acquire()   #wait empty 
    add_data(ide,buffer, sems, index, prod)
    sems[3*ide +1].release()    #signal non empty
    print (f"productor nº{ide} ha acabado de producir")
    
    
def add_data(ide, buffer, sems, index, prod):
    sems[3*ide +2].acquire() #wait mutex(lock)
    try:
        
        buffer[n*ide + index[ide]] = prod   #añadimos producto al buffer
        index[ide] += 1
        #print('Estado del buffer: ' +str(list(buffer)))
    finally:
        sems[3*ide +2].release() #signal mutex(lock) 
        
def get_data(buffer, sems, index,salida):
    lst = []                    #Buscamos el elemento más pequeño
    for i in range(NPROD):
        lst.append(buffer[n*i])
    (minim, ide) = min_buffer(lst)
    sems[3*ide +2].acquire()    #wait mutex(lock)
    try:
        if minim != -1:     #Si es -1 quiere decir que hemos acabado 
            salida.append(minim)
            for i in range(index[ide] -1):  #eliminamos del buffer el elemento
                buffer[n*ide + i]= buffer[n*ide + i + 1] 
            #print('Estado del buffer: ' +str(list(buffer)))
            index[ide] -= 1
        
    finally:
        sems[3*ide + 2 ].release()  #signal mutex(lock)
        return minim, ide, salida
    
    
    
def no_num(n,num=-1):
    return n != num

def min_buffer(lista):          
    mod =  list(filter(no_num, lista))  #obviamos los -1 en la lista
    if mod != []:
        minim= min(mod)
        for i in range(len(lista)):     #recuperamos la posición del minimo
            if lista[i] == minim:
                index = i
                return minim,index
    else:
        return -1,-1
        
        
        
def consumidor (buffer,sems,index):
    minim = 0               #inicialización del bucle while
    salida = []
    for i in range(NPROD):  #comprobamos que todos los productores han generado
        sems[3*i + 1].acquire()     #wait nonEmpty
        
    (minim, ide, salida) = get_data(buffer, sems, index, salida)
    while minim !=-1:
        print (f"consumidor desalmacenando productos del nº {ide}")
        sems[3*ide].release() #signal empty
        print (f"consumidor consumiendo {minim}")
        #print(salida)
        #print(len(salida))
        sems[3*ide + 1].acquire()   #wait nonEmpty
        (minim, ide, salida) = get_data(buffer, sems, index, salida)
    print(salida)
    print('la longitud de la lista es ' + str(len(salida)))
    return salida


def main():
    buffer = Array('i', n*NPROD)    #almacen de los productos
    index = Array('i', NPROD)   #contador del número de productos por productor
    for i in range(NPROD):
        index[i] = 0

    
    sems = []
    for i in range(NPROD):  #generamos la lista de semáforos
        non_empty = Semaphore(0)
        empty = BoundedSemaphore(n)
        mutex = Lock()
        sems.append(empty)
        sems.append(non_empty)
        sems.append(mutex)
    
#GENERAMOS EL PROCESO DE PRODUCTORES
    prodlst = [ Process(target=productor,
                        name=f'prod_{i}',
                        args=(i, buffer, sems, index))
                for i in range(NPROD) ]
#GENERAMOS EL PROCESO DE CONSUMIDOR
    cons=  Process(target=consumidor, args=(buffer, sems, index))
#INICIAMOS PROCESOS
    for p in prodlst:
        p.start()
    cons.start()

    for p in prodlst:
        p.join()
    cons.join()

if __name__ == '__main__':
    main()
