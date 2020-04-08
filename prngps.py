# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 20:01:35 2020

@author: Lukyanov V.S.
"""

# param in: prn_i - number of PRN (SV)
# return: list of code
def prn_gps_L1CA(prn_i):
    if prn_i < 1:
        raise ValueError('PRN must be more 0')
    elif prn_i > 37:
        raise ValueError('todo add support SBAS...')
    # for using as index of list 
    prn_i -= 1
    
    # G1 and G2 sequence (1023-bit Gold-code), init
    G1 = [1] * 10
    G2 = [1] * 10
    
    # generated PRN, init
    prn_list = [0] * 1023
    
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
    ind_xor = [G2_to_G2i[prn_i][0] - 1, G2_to_G2i[prn_i][1] - 1]
    
    
    for i in range(1023):
        prn_list[i] = G1[-1] ^ \
                 ( G2[ind_xor[0]] ^ G2[ind_xor[1]] )
        
        g_new = G1[3 - 1] ^ G1[10 - 1]
        G1 = [ g_new, G1[0:-1] ]
        
        g_new = G2[2 - 1] ^ G2[3 - 1] ^ G2[6 - 1] ^ G2[8 - 1] ^ G2[9 - 1] ^ G2[10 - 1]
        G2 = [ g_new, G2[0:-1] ]
        