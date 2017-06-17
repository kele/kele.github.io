Title: Using Lasagne to achieve over 75% accuracy on CIFAR10.
Date: 2016-01-25
Category: cifar
Tags: neural networks, cifar
lang: en

This is the first report of my battle with the [CIFAR10
classification](https://www.cs.toronto.edu/~kriz/cifar.html) problem.

I've decided to use [Lasagne](http://lasagne.readthedocs.org/en/latest/) which
is a ligthweight library build on top of
[Theano](http://deeplearning.net/software/theano/).

Here's the source code I'll be talking about in this post:
[link](https://github.com/kele/cifar_recognition/tree/over75).

# Overview

* I don't do any data augmentation.
* This piece of code was intended to get me familiarized with Lasagne.
* It achieves slighly over 75% accuracy and I think it's the peak for this
  design of the neural network.

# What is in my toolbox?
My network consists of both dense and convolutional layers. There's a good
reason to use the latter, since they might exploit the nature of our problem
(which is image classification). More on that can be read
[here](http://colah.github.io/posts/2014-07-Conv-Nets-Modular/),
[here](http://colah.github.io/posts/2014-07-Understanding-Convolutions/) and
[here](http://neuralnetworksanddeeplearning.com/chap6.html).

The main intution behind convolutional layers is as follows. We want to detect a
*local* property of an image, i.e. an edge. We don't really care (for now) where
it is, we just want to be sure that it exists. There's no difference in
detecting an edge in the middle of an image or a few pixels to the right.
Because of that, it makes no sense to keep separate parameters (weights and
biases) for different neurons, just because they're looking in some other place
for the same thing.

An additional benefit is the fact that since we're sharing the parameters, there
are less of them to find.


# Architecture
How does the architecture look like?

* Input layer
* 2d Convolutional layer (128 filters of size 5x5, ReLu)
* 2d MaxPool layer (pool size 2x2)
* 2d Convolutional layer (128 filters of size 5x5, ReLu)
* 2d MaxPool layer (pool size 2x2)
* Dropout layer (probability = 0.5)
* Dense layer (256 neurons, ReLu)
* Softmax layer (10 neurons)

# Results
With this architecture I've managed to achieve a little over 75% of accuracy
with around 2 hours of training (on my GT645**M**, which is not a speed demon).

# Roadmap
So, what can we do now?

### Changing the network architecture
So far we can see that my network is pretty shallow. Maybe adding more filters
could help? Also, it might be helpful to put a dense ReLu layer between some
convolution layers. I'll have to experiment with these ideas.

### Better learning techniques
This version of the code doesn't use **weight decay** nor **learning rate**
decay. The only enchancement is the **momentum**. Both of the missing techniques
could be added easily.

These techniques require some additional tuning, so it might be a
little time consuming to find the right parameters. It'd be a good idea to do
that as the last step, after picking a good network architecture.

### Data augmentation
So far I haven't done anything with the input data at all.

The following simple transformations come to my mind:

* cropping the image at random
* horizontal flip
* rescaling

