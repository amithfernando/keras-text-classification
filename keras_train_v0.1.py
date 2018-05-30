from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import os
import sys
import pickle
import numpy as np
from keras_cnn_model import create_model
from keras.utils import to_categorical

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report,confusion_matrix



texts=[]
labels=[]

from pymongo import MongoClient



def read_inputs(folder_name):
	global texts
	global labels
	connection = MongoClient("localhost", 27017)
	db = connection["chatbot"]
	tr_collection=db.trainingData
	class_id = 0
	for document in tr_collection.find():
		intentId = document['intentId']
		patterns = document['patterns']
		texts = texts + patterns
		for p in patterns:
			labels.append(class_id)
		class_id += 1

# def read_inputs(folder_name):
# 	global texts
# 	global labels
# 	dirs=os.listdir(folder_name)
# 	class_id=0
# 	for fn in dirs:
# 		print("Processing {}".format(fn))
# 		full_path = os.path.join(folder_name,fn)
# 		fh=open(full_path)
# 		lines=fh.readlines()
# 		fh.close()
# 		texts = texts+lines
# 		[labels.append(class_id) for x in lines]
# 		class_id += 1

if __name__ == '__main__':
	read_inputs('./data')
	tokenizer = Tokenizer(num_words=500)
	tokenizer.fit_on_texts(texts)
	sequences = tokenizer.texts_to_sequences(texts)
	word_index = tokenizer.word_index
	vocab_size = len(word_index)
	data=pad_sequences(sequences,maxlen=50)
	print("Length of training data {}".format(len(data)))
	print("Shape of data {}".format(data.shape))
	indices = np.arange(data.shape[0])
	#np.random.shuffle(indices)
	#print("Indices {}".format(indices))
	#data = data[indices]
	labels = np.array(labels)
	labels_cat = to_categorical(labels)
	#labels = to_categorical(np.asarray(labels))  # this converts [0,0,1,1] to [[1..],[1...],[0 1 0...]..]
	#print(labels)
	#labels = labels[indices]


	kfold = StratifiedKFold(n_splits=30, shuffle=True, random_state=12)
	cvscores = []
	models=[]
	test_data=[]

	""" Ready to train """
	print(" data shape {}".format(data.shape))
	print(" train shape {}".format(labels.shape))
	for train,test in kfold.split(data,labels):
		# As keras does not have support for multi filters in cnn on same output from embedding layer hence proceeding with one layer of cnn with one filte
		Y = labels_cat[train]	
		Y_test = labels_cat[test]
		model = create_model(vocab_size,100,50,(3,),256,0.3)
		model.fit(data[train],Y,epochs=80,batch_size=16)
		scores = model.evaluate(data[test],Y_test,verbose=1)
		print("{} {}".format(model.metrics,scores))
		cvscores.append(scores[2])
		models.append(model)
		test_data.append(test)
	print(cvscores)
	max_index=np.array(cvscores).argmax()
	model = models[max_index]
	t_data = test_data[max_index]
	predicted = model.predict(data[t_data])
	print(np.round(predicted))
	print(labels_cat[t_data])
	print(classification_report(labels_cat[t_data],np.round(predicted)))
	print(confusion_matrix(np.argmax(labels_cat[t_data],axis=1),np.argmax(np.round(predicted),axis=1)))
	#cvscores.append(scores)
	#model.save('./keras_saved_model/intent_model.2.h5')
	#pickle.dump(tokenizer,open('./keras_saved_model/tokenizer.2.p','wb'))
