Title: CIFAR10 classification summary
Date: 2016-03-04
Category: neural networks

#Problem description
[CIFAR10](https://www.cs.toronto.edu/~kriz/cifar.html) classification is a very popular problem among neural networks enthusiast. The main task is to map 32x32 RGB images to (disjoint) classes. This (simple) version of the problem differentiates 10 classes (hence the name).

A list of best results for this problem can be found [here](http://rodrigob.github.io/are_we_there_yet/build/classification_datasets_results.html)

As one can guess, this problem is significantly harder than MNIST, both because of the input size and the nature of the images (two pictures of cats can be very different, but a digit always has roughly the same shape).

The CIFAR10 dataset consists of 60000 32x32 colour images in 10 classes, with 6000 images per class. There are 50000 training images and 10000 test images. 

#Network architecture
Since the dataset is a collection of 2D images, using convolutional neural networks seem to be a good place to start. This is because of the fact that CNNs are able to learn to detect some local properties of the input, by looking at a patch of data at once. This is not only vital for doing any image processing work (i.e. edge detection), but it can greately decrease the size of the NN, since neurons used to detect a single feature share parameters (weights).

#How the training is done?
##Technique
Stochastic gradient descent (with mini batches) is used as a standard learning technique.
##Epochs
The training set is divided into epochs of a size of 40000 images, after each a validation set of size 10000 is used. The data is split into mini batches.
##Mini batches
Mini batches of size 100 are used. Using less than that seems to be a bad idea, since we have 10 classes and we would like to see at least a few examples of each class in one mini batch. Using more than that might speed up the computation on GPUs, but because of the choice of the learning technique (SGD), it might actually take longer to learn (fewer steps).
##Data preparation
The data is scaled and shifted to fit in [-1; +1] range.

#Report
## Getting around 75% accuracy
This is a sample network architecture that is able to quickly learn to solve our problem achieving around 75% accuracy on the test dataset.

- Input layer
- 2d Convolutional layer (128 filters of size 5x5, ReLu)
- 2d MaxPool layer (pool size 2x2)
- 2d Convolutional layer (128 filters of size 5x5, ReLu)
- 2d MaxPool layer (pool size 2x2)
- Dropout layer (probability = 0.5)
- Dense layer (256 neurons, ReLu)
- Softmax layer (10 neurons)

This simple architecture deservers a short explanation.

ReLu is used as the activation function for the obvious reasons (efficient computation, no vanishing gradient, etc.). At the moment of writing this report, it seems to be the most popular activation function for NNs.

An affine (dense) layer is introduced near the end of the network for simplicity. Although, all-convolutional NNs are possible (<http://arxiv.org/abs/1412.6806>), their design is a little more sophisticated.

As for mitigating the risks of overfitting, early stopping with a validation set is used. The second tool helping to deal with this phenomena is the dropout.

##Getting over 75% accuracy
###Techniques used to improve the learning process
The architecture mentioned in previous chapter is probably not suitable for getting statistically significant over 75% accuracy without a bit of luck.

Since the network is not that small, there is a risk of overfitting. Besides dropout, weight decay (L2 regularization) and momentum are used.

Learning rate decay is used as a standard approach to improve both the speed and the effectiveness of the process.
###Architecture
This architecture together with mentioned improvements can be used to achieve 78% test accuracy within just 25 epochs of training. One epoch took around 15s on GeForce GTX 780 GPU, which sums up to less than 7 minutes of training.

- Input layer
- 2d Convolutional layer (128 filters of size 5x5, ReLu)
- 2d MaxPool layer (pool size 2x2)
- __2d Convolutional layer (64 filters of size 5x5, ReLu)__
- 2d MaxPool layer (pool size 2x2)
- __Dropout layer (probability = 0.5)__
- __Dense layer (800 neurons, ReLu)__
- Dropout layer (probability = 0.5)
- Dense layer (256 neurons, ReLu)
- Softmax layer (10 neurons)

It seems that keeping two big convolutional layers was not needed. On the other hand, introducing an additional affine layer helped achieving better accuracy. Adding more dropout layers seems to introduce too much noise to make the learning process efficient.
###Hyperparameters
The hyperparamers were found by trial and error.

The learning rate decay formula:

- start: 0.01
- divide by 1.5 after 4000 mini batches

Momentum: 0.9.

Weight decay: 0.01.

##Getting over 80% accuracy
###Data augmentation
Introducing random horizontal flip (mirror, left to right) improved the accuracy to over 80% after less than 60 epochs (with the same epoch computation time as before, 15 seconds).

##Getting 81.72% accuracy
Data augmentation
Adding a random rotation between [-20; +20] degrees allowed to achieve 81.72% accuracy on the test dataset without increasing the learning time.

#Implementation details
A lightweight library built on top of [Theano](http://deeplearning.net/software/theano/) called [Lasagne](https://github.com/Lasagne/Lasagne) was used for the implementation. The source code is available here: <https://github.com/kele/cifar_recognition/>. Using it is pretty straightforward and I highly recommend this as a base for any neural networks project.
#Future work
##Deeper neural network
A deeper neural network could be used to improve the results. On the other hand, that might introduce even bigger risk of overfitting and greately increase the learning time.
##Data augmentation
Data augmentation proved to be very helpful for solving the CIFAR10 problem. The solutions described in this report could take advantage of image transformations such as ZCA. Also, using slight shifts and rotations, or random crops of the image could be used to artificially enlarge the training dataset.
#Conclusion
One can easily solve the CIFAR10 classification problem with a decent accuracy using widely available Python libraries. The only caveat is the fact that deep neural networks might require efficient, CUDA-capable GPUs to work (and learn) fast.

