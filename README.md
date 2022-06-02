# Hindi Music Based Induced Emotion Classification

<p align="center">
  <img width="900" height="250" src="https://user-images.githubusercontent.com/54277039/171614782-50db1671-13e7-4037-8327-4ada885938cd.png">
</p>

This repository focuses on the internal working of Pre-Trained Convolutional Neural Networks (CNNs), with different architectures as follows:-

1. AlexNet :- It has 8 layers with learnable parameters. The model consists of 5 layers with a combination of Max Pooling followed by 3 fully connected layers and they use Relu activation in each of these layers, except the output layer.
2. VGG-16:- It was proposed by Karen Simonyan and Andrew Zisserman in 2014 in the paper "Very Deep Convolutional Networks for Large Scale Image Recognition".
3. MobileNetV3-Small :- It is a simple but efficient and not very computationally intensive convolutional neural network for mobile vision applications.
4. ResNet-18 :- It is a convolutional neural network that is 18 layers deep. ResNet includes several residual blocks that consist of convolutional layers, batch normalization layers and ReLU activation functions. We used the pretrained ResNet50 model to extract features from the Human Faces.
5. DenseNet-121 :- It has 120 Convolutions and 4 Average Pooling Layers, thereby requiring fewer parameters and allowing feature reuse. It resulted in more compact modelling and achieving SOTA performances and better results across competitive datasets, compared to their standard CNN or ResNet counterparts.
6. EfficientNet-B0 :- They are very much computationally efficient and also achieve SOTA results on ImageNet dataset, which is 84.4% on Top-1 Accuracy. It was developed using a Multi-Objective Neural Architecture Search that optimizes both accuracy and floating-point operations.

The MER500 Dataset consist of songs in 5 popular emotional categories for Hindi-Film Industry such as Romantic, Happy, Sad, Devotional and Party. It has approximately 100 Audio Files of about 10 seconds of Song-Clips per class label. 

As far as the fine-tuning configurations are in concern, the following were performed:-

1. The Input Audio Data was sampled at frequency of 16KHz and padded via shorter sliding windows, following by normalization to single-peak central gaussian distribution.
2. The representation of the Audio-Signals into Image-based Data was done via Mel-Spectrograms.
3. Train-Test Split was defined to 80-20, Batch-Size was set to 64 for best set of results and Number of Epochs were set to 5.  
