#SYSCALLS TO MONITOR FOR ARGS
SYSCALLS_ARGS = ['open', 'stat', 'clone', 'execve']

#FOLD INCREASE (FI)
BETA_FOLD_INCREASE = 5

#SEQUENCE DURATION
SEQUENCE_DURATION = '1s'


# LEARNING
EPOCH = 120
OPTIMIZER = 'Adam'
LOSS_FUNC = 'mse'
BATCH_SIZE = 50
VALIDATION_SPLIT = 0.2
ACTIVATION = 'sigmoid'
REG_RATE = 0.01
ENCODING_DIM = DECODING_DIM = 2
BOTTLENECK = 1
VERBOSE = 1


THETA_VALUES = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]

#NUMBER OF DIRECTORIES FOR DISCARDING FILENAMES
PATH_LENGTH = 3


#MULTIPROCESSING
CHUNK_SIZE=50