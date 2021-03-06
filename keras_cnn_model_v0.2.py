from keras.layers import Conv1D, MaxPooling1D , Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.core import Flatten
from keras.models import Sequential
from keras.optimizers import Adam
import keras

def create_model(vocab_size,embedding_size,max_sentence_length,filter_sizes,num_filters,dropout,embedding_matrix=None):
	model = Sequential()
	if embedding_matrix is None:
		model.add(Embedding(vocab_size+1,embedding_size,input_length=max_sentence_length))
	else:
		model.add(Embedding(vocab_size+1,embedding_size,weights=[embedding_matrix],input_length=max_sentence_length,trainable=False))
	#for filter_size in filter_sizes:
	#model.add(Dense(50,activation='softmax'))
	#model.add(Conv1D(num_filters,3,activation='relu',padding="same"))
	model.add(Conv1D(num_filters,1,activation='tanh'))
	model.add(MaxPooling1D(pool_size=(3,),strides=1))
	model.add(Dropout(dropout))
	model.add(Conv1D(num_filters*2,2,activation='relu'))
	model.add(MaxPooling1D(pool_size=(2,),strides=1))
	model.add(Dropout(dropout))
	model.add(Flatten())
	model.add(Dense(256,activation='tanh'))
	model.add(Dropout(dropout))
	model.add(Dense(128,activation='tanh'))
	model.add(Dense(6,activation='softmax'))
	#model.add(Activation('softmax'))
	#model.compile(loss=keras.losses.categorical_crossentropy,optimzer=keras.optimizers.SGD(),metrics=['accuracy'])
	adam = Adam(lr=0.0001, decay=1e-5)
	model.compile(loss='categorical_crossentropy',optimizer=adam,metrics=['mse', 'acc'])
	return model
