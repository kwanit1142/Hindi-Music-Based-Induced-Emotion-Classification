# Hindi Music Based Induced Emotion Classification

<p align="center">
  <img width="450" height="350" src= "https://user-images.githubusercontent.com/54277039/174309785-875c3144-4353-422a-b3ee-dac2b3c9d209.jpg">
</p>
                                      
Music has always been a huge part of our quotidian routine. The kind of music we listen to has a stronghold on our emotional core. The signals delivered by the audio-snippets from a class of music could be captured and are visually represented as a plot between different frequency signatures with respect to time-stamp as spectrogram. On the heatmaps generated, we can distinguish the power of different patched of the music based on the intensity of those regions. 

## About

In this repository, we propose an end-to-end pipeline for identifying the type of emotions induced by different genres of music by studying the mel-spectrogram of audio-snippets from Hindi Music obtained from the publicly available MER500 dataset on Kaggle. By employing dfifferent pre-trained CNN architectures, the audio snippets are pre-processed to extract the corresponding feature-space and passed as input to them.

## Dataset

The `MER500 Dataset` consist of songs in 5 popular emotional categories for Hindi-Film Industry such as:- 

1. Romantic 
2. Happy 
3. Sad 
4. Devotional 
5. Party 

It has approximately `100 Audio Files` of about `10 seconds` of Song-Clips per class label.

## Models

This repository focuses on the internal working of Pre-Trained Convolutional Neural Networks (CNNs), with different architectures as follows:-

1. `AlexNet` :- It has 8 layers with learnable parameters. The model consists of 5 layers with a combination of Max Pooling followed by 3 fully connected layers and they use Relu activation in each of these layers, except the output layer.

![Screenshot (1292)](https://user-images.githubusercontent.com/54277039/174310615-fd492ecb-3c58-4c12-ad14-700517ae90b7.png)

2. `VGG-16` :- It was proposed by Karen Simonyan and Andrew Zisserman in 2014 in the paper "Very Deep Convolutional Networks for Large Scale Image Recognition".

![Screenshot (1291)](https://user-images.githubusercontent.com/54277039/174310675-4afcc0f6-efdc-448f-88fc-73395333b777.png)

3. `MobileNetV3-Small` :- It is a simple but efficient and not very computationally intensive convolutional neural network for mobile vision applications.

![Screenshot (1296)](https://user-images.githubusercontent.com/54277039/174310691-7a69a4e1-d7a1-4bd7-bed7-72d39d1b7b3a.png)

4. `ResNet-18` :- It is a convolutional neural network that is 18 layers deep. ResNet includes several residual blocks that consist of convolutional layers, batch normalization layers and ReLU activation functions. We used the pretrained ResNet50 model to extract features from the Human Faces.

![Screenshot (1295)](https://user-images.githubusercontent.com/54277039/174310730-e0d4ef0d-7a25-4b9d-ba60-aad71fac4f98.png)

5. `DenseNet-121` :- It has 120 Convolutions and 4 Average Pooling Layers, thereby requiring fewer parameters and allowing feature reuse. It resulted in more compact modelling and achieving SOTA performances and better results across competitive datasets, compared to their standard CNN or ResNet counterparts.

![Screenshot (1297)](https://user-images.githubusercontent.com/54277039/174310763-98a5b208-2655-4c1a-b419-cc0ad4dc1fe5.png)

6. `EfficientNet-B0` :- They are very much computationally efficient and also achieve SOTA results on ImageNet dataset, which is 84.4% on Top-1 Accuracy. It was developed using a Multi-Objective Neural Architecture Search that optimizes both accuracy and floating-point operations.   

![Screenshot (1293)](https://user-images.githubusercontent.com/54277039/174310782-ab0d3ccb-cf25-4181-84b7-cea3bd2bb003.png)

## End-To-End Pipeline

<p align="center">
  <img width="900" height="250" src="https://user-images.githubusercontent.com/54277039/171614782-50db1671-13e7-4037-8327-4ada885938cd.png">
</p>

As far as the fine-tuning configurations are in concern, the following were performed:-

1. The Input Audio Data was sampled at `frequency of 16KHz` and `padded via shorter sliding windows`, following by `normalization` to single-peak central gaussian distribution.

2. The representation of the Audio-Signals into Image-based Data was done via `Mel-Spectrograms`.

3. `Train-Test Split` was defined to `80-20`, `Batch-Size` was set to `64` for best set of results and `Number of Epochs` were set to `5` for quick results.

## Evaluation

![Screenshot (1294)](https://user-images.githubusercontent.com/54277039/174310836-e55449cd-be28-4b10-8244-80666f9be87d.png)

# Contributors

1. [Hiteshi Singh](https://github.com/hiteshidudeja)
2. [Divyanshi Jagetiya](https://github.com/divyyanshii)
3. [Kwanit Gupta (me)](https://github.com/kwanit1142)
