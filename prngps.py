# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 20:01:35 2020

@author: Lukyanov V.S.
"""

import copy

# list pf signal's consts

# length of L1CA PRN 
Len_prn_L1CA = 1023
# length of L2CM PRN 
Len_prn_L2CM = 10230
# length of L2CM PRN
Len_prn_L2CL = 767250

# Lengt of bitof mavigation msg
Nav_bit_L2CM = 20e-3

L2C_polynomial = [3,4,5,6,9,11,13,16,19, 21, 24, 27]
L2C_len_gen    = 27



def numToList(x, n):
    lst = [0] * n
    for k in range(n):
        lst[k] = (x>>k) & 0x1
    return lst

def listToNum(lst):
    x = 0;
    for k in range(len(lst)):
        x += (lst[k] << k)
    return x

# generators

def genL1CA(prn):
    """ C/A code generation

param in: prn - number of PRN (SV)
return: list of code
    """
    if prn < 1:
        raise ValueError('PRN must be more 0')
    elif prn > 37:
        raise ValueError('todo add support SBAS...')
    
    
    # G1 and G2 sequence (1023-bit Gold-code), init
    G1 = [1] * 10
    G2 = [1] * 10
    
    # generated PRN, init
    prn_list = [0] * Len_prn_L1CA
    
    # table for converting a sequence G2 to G2i
    G2_to_G2i = [ [ 2,  6], # 1
                  [ 3,  7],
                  [ 4,  8],
                  [ 5,  9],
                  [ 1,  9], # 5
                  [ 2, 10], 
                  [ 1,  8],
                  [ 2,  9],
                  [ 3, 10],
                  [ 2,  3], # 10
                  [ 3,  4],
                  [ 5,  6],
                  [ 6,  7],
                  [ 7,  8],
                  [ 8,  9], # 15
                  [ 9, 10],
                  [ 1,  4],
                  [ 2,  5],
                  [ 3,  6],
                  [ 4,  7]  # 20
                  ]
    # for using as index of list 
    prn_i = prn - 1
    ind_xor = [G2_to_G2i[prn_i][0] - 1, G2_to_G2i[prn_i][1] - 1]
    
    
    for i in range(Len_prn_L1CA):
        prn_list[i] = G1[-1] ^ \
                 ( G2[ind_xor[0]] ^ G2[ind_xor[1]] )
        
        g_new = G1[3 - 1] ^ G1[10 - 1]
        G1 =  [g_new] + G1[0:-1]
        
        g_new = G2[2 - 1] ^ G2[3 - 1] ^ G2[6 - 1] ^ G2[8 - 1] ^ G2[9 - 1] ^ G2[10 - 1]
        G2 = [g_new] + G2[0:-1]
    return prn_list


def _genL2C(reg_list, Len):
    prn_list = [0] * Len;
    #print(oct(listToNum(reg_list)))
    for i in range(Len):
    #    if i == Len - 1:
    #        print(oct(listToNum(reg_list)))
        new_val = reg_list[0]
        prn_list[i] = new_val
        #register update
        for k in range(L2C_len_gen-1):     
            if (k+1) in L2C_polynomial:
                reg_list[k] = reg_list[k + 1] ^ new_val
            else:
                reg_list[k] = reg_list[k + 1]
        reg_list[-1] = new_val 
    return prn_list
        

def genL2C(prn, tSignal = 'L2CM', nav_data = [1, 0]):
    """code generator for L2CL or L2CM or L2CM+L2CL signals
    
param in: prn - number of PRN (SV)
param in: tSignal - type of signal: L2CL, L2CL, L2C (for L2CL + L2CM)
param in: nav_data - data for L2CM, valid value [1, 1], [0,0] - const, [1, 0], [0, 1] - meander
return: list of code
    """
    if prn < 1 or prn > 32:
        raise ValueError('PRN must be more > 0 and < 32')
    
    
    if tSignal == 'L2CM' or tSignal == 'L2C':
        if prn == 1:
             reg_init = numToList(int('742417664', 8), L2C_len_gen)
        elif prn == 2:
            reg_init = numToList(int('756014035', 8), L2C_len_gen)
        elif prn == 3:
            reg_init = numToList(int('002747144', 8), L2C_len_gen)
        elif prn == 4:
            reg_init = numToList(int('066265724', 8), L2C_len_gen)
        elif prn == 5:
            reg_init = numToList(int('601403471', 8), L2C_len_gen)
        else:
            print('error: undef case...')
            1/0#error
        
        prn_list_l2cm = _genL2C(reg_init, Len_prn_L2CM)
        if tSignal == 'L2CM':
            return prn_list_l2cm
    
    if tSignal == 'L2CL' or tSignal == 'L2C':
        if prn == 1:
            reg_init = numToList(int('624145772', 8), L2C_len_gen)
        elif prn == 2:
            reg_init = numToList(int('506610362', 8), L2C_len_gen)
        elif prn == 3:
            reg_init = numToList(int('220360016', 8), L2C_len_gen)
        elif prn == 4:
            reg_init = numToList(int('710406104', 8), L2C_len_gen)
        elif prn == 5:
            reg_init = numToList(int('001143345', 8), L2C_len_gen)
        else:
            print('error: undef case...')
            1/0#error
        
        prn_list_l2cl = _genL2C(reg_init, Len_prn_L2CL)
        if tSignal == 'L2CL':
            return prn_list_l2cl
    # L2CL + L2CM
    # На перидоде L2CL формируем суммарный сигнал  
    prn_list = [0]*(Len_prn_L2CL*2)
    for k in range(Len_prn_L2CL):
        # The first L2CM, then L2LM
        prn_list[2*k    ] = prn_list_l2cm[k % Len_prn_L2CM] ^ nav_data[k % 2]
        prn_list[2*k + 1] = prn_list_l2cl[k               ]
    return prn_list
    
    
    
    