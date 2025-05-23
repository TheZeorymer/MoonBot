# distutils: language = c++
import numpy as np
cimport numpy as np
from libc.stdint cimport uint64_t

cdef class BitboardMoonBot:
    cdef np.ndarray[np.uint64_t, ndim=1] white_pieces
    cdef np.ndarray[np.uint64_t, ndim=1] black_pieces
    cdef int turn  # 0=white, 1=black

    def __init__(self):
        self.white_pieces = np.zeros(6, dtype=np.uint64)
        self.black_pieces = np.zeros(6, dtype=np.uint64)
        self.turn = 0
        # TODO: initialize bitboards for starting position

    cpdef int evaluate(self):
        cdef int score = 0
        # TODO: implement fast bitwise evaluation
        return score

    cpdef tuple negamax(self, int depth, int alpha, int beta):
        # TODO: implement fast bitboard negamax search
        return (0, None)

    cpdef list generate_legal_moves(self):
        # TODO: implement fast bitboard move generation
        return []

    cpdef void push(self, int move):
        # TODO: update bitboards for move
        pass

    cpdef void pop(self):
        # TODO: undo last move
        pass
