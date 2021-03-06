import os
import glob
import numpy as np
import cv2
from sklearn.utils import shuffle


def load_train(train_path, image_size, classes):
    images = []
    labels = []
    ids = []
    cls = []

    print('Reading training images')
    for fld in classes:   # assuming data directory has a separate folder for each class, and that each folder is named after the class
        index = classes.index(fld)
        print('Loading {} files (Index: {})'.format(fld, index))
        path = os.path.join(train_path, fld, '*g')
        files = glob.glob(path)
        for fl in files:
            image = cv2.imread(fl)[:,:,0]  #abre la imagen
            f = cv2.threshold(image,127,1,cv2.THRESH_BINARY)
            images.append(f[1]) 
            label = np.zeros(len(classes)) # crea un arreglo en 0 con la cantidad de clases que hay
            label[index] = 1.0 # coloca en una el tipo de clase que es la imagen
            labels.append(label)
            flbase = os.path.basename(fl) # obtiene el nombre de la foto
            ids.append(flbase) 
            cls.append(fld) # las clases

    images = np.array(images)
    labels = np.array(labels)
    ids = np.array(ids)
    cls = np.array(cls)

    return images, labels, ids, cls

def load_test(test_path, image_size):
    path = os.path.join(test_path, '*ng')
    files = sorted(glob.glob(path))

    X_test = []
    X_test_id = []
    print("Reading test images")
    for fl in files:
        flbase = os.path.basename(fl)
        image = cv2.imread(fl)[:,:,0]
        f = cv2.threshold(image,127,1,cv2.THRESH_BINARY)
        X_test.append(f[1]) 
        X_test_id.append(flbase)

    ### because we're not creating a DataSet object for the test images, normalization happens here
    X_test = np.array(X_test, dtype=np.uint8)

    return X_test, X_test_id

class DataSet(object):

  def __init__(self, images, labels, ids, cls):
    """Construct a DataSet. one_hot arg is used only if fake_data is true."""

    self._num_examples = images.shape[0]

    # Convert shape from [num examples, rows, columns, depth]
    # to [num examples, rows*columns] (assuming depth == 1)
    # Convert from [0, 255] -> [0.0, 1.0].

    images = images.astype(np.bool_) #casting a float32
    # images = np.multiply(images, 1.0 / 255.0)

    self._images = images
    self._labels = labels
    self._ids = ids
    self._cls = cls
    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def images(self):
    return self._images

  @property
  def labels(self):
    return self._labels

  @property
  def ids(self):
    return self._ids

  @property
  def cls(self):
    return self._cls

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def next_batch(self, batch_size):
    """Return the next `batch_size` examples from this data set."""
    start = self._index_in_epoch
    self._index_in_epoch += batch_size

    if self._index_in_epoch > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      #print("index epoch = {0}\nnum examples = {1}\n".format(self._index_in_epoch, self._num_examples))
      # # Shuffle the data (maybe)
      # perm = np.arange(self._num_examples)
      # np.random.shuffle(perm)
      # self._images = self._images[perm]
      # self._labels = self._labels[perm]
      # Start next epoch

      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_examples, "Number of examples in less than batch\n"
    end = self._index_in_epoch

    return self._images[start:end], self._labels[start:end], self._ids[start:end], self._cls[start:end]


def read_train_sets(train_path, image_size, classes, validation_size=0):
  class DataSets(object):
    pass
  data_sets = DataSets()

  images, labels, ids, cls = load_train(train_path, image_size, classes)
  images, labels, ids, cls = shuffle(images, labels, ids, cls)  # shuffle the data

  #Data dividing
  #validation_size is a percentage
  #Image.shape[0] is the number of rows 
  if isinstance(validation_size, float):
    validation_size = int(validation_size * images.shape[0])

  #Validation data
  validation_images = images[:validation_size]
  validation_labels = labels[:validation_size]
  validation_ids = ids[:validation_size]
  validation_cls = cls[:validation_size]

  #Training data
  train_images = images[validation_size:]
  train_labels = labels[validation_size:]
  train_ids = ids[validation_size:]
  train_cls = cls[validation_size:]

  data_sets.train = DataSet(train_images, train_labels, train_ids, train_cls)
  data_sets.valid = DataSet(validation_images, validation_labels, validation_ids, validation_cls)

  return data_sets

def read_train_validation_sets(train_path, image_size, classes, validation_size=0):
  class DataSets(object):
    pass
  data_sets = DataSets()

  images, labels, ids, cls = load_train(validation_path, image_size, classes)
  images, labels, ids, cls = shuffle(images, labels, ids, cls)  # shuffle the data

  #Training data
  train_images = images
  train_labels = labels
  train_ids = ids
  train_cls = cls

  data_sets.train = DataSet(train_images, train_labels, train_ids, train_cls)

  return data_sets


def read_test_set(test_path, image_size):
  images, ids  = load_test(test_path, image_size)
  return images, ids
