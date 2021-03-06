# -*- coding: utf-8 -*-
"""DL_Project_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19SW7IgCU_GblRurYVD9ybVjL1QHBOD0g
"""

cd /content/drive/MyDrive/DL_Project_2

import zipfile
import pandas as pd
import librosa as lib
from tqdm import tqdm
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import librosa as lib
import torch
from torchvision import datasets, transforms, models
from torch.utils.data import Dataset
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device

"""#Data-related Code Snippets"""

with zipfile.ZipFile('/content/drive/MyDrive/DL_Project_2/archive.zip', 'r') as zip_ref:
  zip_ref.extractall('/content/drive/MyDrive/DL_Project_2')

def rename_files(root_path):
  for emotion in ["Sad","Romantic","Devotional","Party","Happy"]:
    emotional_path = os.path.join(root_path,str(emotion)+'/'+str(emotion))
    list_emotional = os.listdir(emotional_path)
    for emotion_piece in list_emotional:
      piece = os.path.join(emotional_path,emotion_piece)
      new_piece = os.path.join(emotional_path,emotion+str("_")+emotion_piece)
      os.rename(piece, new_piece)
    print("done")

rename_files('/content/drive/MyDrive/DL_Project_2')

def dataframe_creation(root_path):
  label=0
  audio_name = []
  label_list = []
  for emotion in ["Sad","Romantic","Devotional","Party","Happy"]:
    emotional_path = os.path.join(root_path,str(emotion)+'/'+str(emotion))
    list_emotional = os.listdir(emotional_path)
    for emotion_piece in list_emotional:
      piece = os.path.join(emotional_path,emotion_piece)
      audio_name.append(piece)
      label_list.append(label)
    label = label+1
  df = pd.DataFrame(columns=["Audio_Name","Emotion_Name"])
  df["Audio_Name"] = audio_name
  df["Emotion_Name"] = label_list
  return df

audio_df = dataframe_creation('/content/drive/MyDrive/DL_Project_2')

audio_df.to_csv('/content/drive/MyDrive/DL_Project_2/Audio_metafile.csv')

"""#Main Function"""

audio_df = pd.read_csv('/content/drive/MyDrive/DL_Project_2/Audio_metafile.csv')

audio_df

audio_df = audio_df.drop(columns=['Unnamed: 0'])

sample_1 = lib.load(audio_df["Audio_Name"][0])
x,y = sample_1
x.shape

hl = 512 # number of samples per time-step in spectrogram
hi = 224 # Height of image
wi = 224 # Width of image

window = x[0:wi*hl]

S = lib.feature.melspectrogram(y=window, sr=y, n_mels=hi, fmax=8000, hop_length=hl)
S_dB = lib.power_to_db(S, ref=np.max)

plt.imshow(S_dB)

"""# Dataset Class and Function"""

from torch.utils.data.sampler import SubsetRandomSampler

class Data_Prepare(Dataset):
  """
  The Class will act as the container for our dataset. It will take your dataframe, the root path, and also the transform function for transforming the dataset.
  """
  def __init__(self, data_frame, transform=None):
    self.data_frame = data_frame
    self.transform = transform
    self.hl = 512 # number of samples per time-step in spectrogram
    self.hi = 224 # Height of image
    self.wi = 224 # Width of image
  def __len__(self):
    # Return the length of the dataset
    return len(self.data_frame)
  def __getitem__(self, idx):
    # Return the observation based on an index. Ex. dataset[0] will return the first element from the dataset, in this case the image and the label.
    if torch.is_tensor(idx):
      idx = idx.tolist()    
    audio_name = self.data_frame.iloc[idx, 0]
    audio_file, y = lib.load(audio_name)
    audio_window = audio_file[0:self.wi*self.hl]
    spectrogram = lib.feature.melspectrogram(y=audio_window, sr=y, n_mels=self.hi, fmax=8000, hop_length=self.hl)
    plot = lib.power_to_db(spectrogram, ref=np.max)
    plot = cv2.resize(cv2.cvtColor(plot,cv2.COLOR_GRAY2RGB),(224,224))
    label = (self.data_frame.iloc[idx, -1])
    if self.transform:
      plot = self.transform(plot)
    return (plot, label)

def data_preparation(Data_Class, Dataframe, Mean, Std, Batch_Size = 128, Shuffle = False):
  transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize(Mean, Std)])
  dataset_whole = Data_Class(data_frame=Dataframe,transform = transform)
  test_split = 0.2
  random_seed= 42
  dataset_size = len(dataset_whole)
  indices = list(range(dataset_size))
  split = int(np.floor(test_split * dataset_size))
  if Shuffle==True:
    np.random.seed(random_seed)
    np.random.shuffle(indices)
  train_indices, test_indices = indices[split:], indices[:split]
  train_sampler = SubsetRandomSampler(train_indices)
  test_sampler = SubsetRandomSampler(test_indices)
  train_loader = torch.utils.data.DataLoader(dataset = dataset_whole, batch_size = Batch_Size, pin_memory = True, num_workers=2, sampler=train_sampler)
  test_loader = torch.utils.data.DataLoader(dataset = dataset_whole, batch_size = Batch_Size, pin_memory = True, num_workers=2, sampler=test_sampler)
  return train_loader, test_loader

train, test = data_preparation(Data_Prepare, audio_df,(0,0,0),(1,1,1),Batch_Size=64, Shuffle=True)

"""# Helper Function"""

def bifurcation(model_name):
  model = model_name(pretrained=True)
  param = model.state_dict()
  for i in param.keys():
    print(i)

def selective_finetuning_single_layer(model_name, layer_name):
  model = model_name(pretrained=True)
  for name, param in model.named_parameters():
    if param.requires_grad and layer_name in name:
      param.requires_grad = True
    else:
      param.requires_grad = False
  optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()))
  return model.cuda(), torch.nn.CrossEntropyLoss().cuda(), optimizer

def grad_change(Loss_Function, Optimizer, Label = None, Predicted = None):
  Optimizer.zero_grad()
  loss = Loss_Function(Predicted, Label)
  loss.backward()
  Optimizer.step()
  return loss, Optimizer

def model(Train_Loader, Test_Loader, Epochs, Model_Class=None, Loss_Function=None, Optimizer=None):
  outputs_train=[]
  outputs_test=[]
  y_true=[]
  y_pred=[]
  for Epoch in range(Epochs):
    running_loss_train=0
    running_loss_test=0
    correct_train=0
    correct_test=0
    for (image, label) in tqdm(Train_Loader):
      image = image.cuda()
      label = torch.tensor(label).cuda()
      out = Model_Class(image)
      loss, Optimizer = grad_change(Loss_Function = Loss_Function, Optimizer = Optimizer, Label = label, Predicted = out)
      running_loss_train += loss.item()
      predicted_train = out.data.max(1, keepdim=True)[1]
      correct_train += predicted_train.eq(label.data.view_as(predicted_train)).sum()
      outputs_train.append((Epoch, running_loss_train/len(Train_Loader.dataset), 100*correct_train/len(Train_Loader.dataset)))
    with torch.no_grad():
      for (image, label) in Test_Loader:
        image = image.cuda()
        label = torch.tensor(label).cuda()
        out = Model_Class(image)
        loss = Loss_Function(out,label)
        running_loss_test += loss.item()
        predicted_test = out.data.max(1, keepdim=True)[1]
        if Epoch==(Epochs-1):
          y_pred.extend(predicted_test.cpu().numpy())
          y_true.extend(label.data.cpu().numpy())
        correct_test += predicted_test.eq(label.data.view_as(predicted_test)).sum()
        outputs_test.append((Epoch, running_loss_test/len(Test_Loader.dataset), 100*correct_test/len(Test_Loader.dataset)))
  return Model_Class, outputs_train, outputs_test, y_pred, y_true

"""# VGG16 Training and Inference"""

bifurcation(models.vgg16)

import warnings
warnings.filterwarnings("ignore")

model_vgg16, loss_vgg16, optim_vgg16 = selective_finetuning_single_layer(models.vgg16, 'classifier')
model_vgg16 ,vgg16_train ,vgg16_test, vgg16_pred, vgg16_true = model(train,test,5,model_vgg16, loss_vgg16, optim_vgg16)

import seaborn as sns 
from sklearn.metrics import confusion_matrix
cf_matrix=confusion_matrix(vgg16_true,vgg16_pred)
cf_matrix

plt.figure(figsize=(9,9))
sns.heatmap(cf_matrix, cbar=False, fmt='d', annot=True, cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix of the CNN Classifier')
plt.show()

"""# Mobilenet-V3-Small Training and Inference"""

bifurcation(models.mobilenet_v3_small)

model_mobilenet_v3_small, loss_mobilenet_v3_small, optim_mobilenet_v3_small = selective_finetuning_single_layer(models.mobilenet_v3_small, 'classifier')
model_mobilenet_v3_small ,mobilenet_v3_small_train ,mobilenet_v3_small_test, mobilenet_v3_small_pred, mobilenet_v3_small_true = model(train,test,5,model_mobilenet_v3_small, loss_mobilenet_v3_small, optim_mobilenet_v3_small)

cf_matrix_mobilenet=confusion_matrix(mobilenet_v3_small_true,mobilenet_v3_small_pred)
cf_matrix_mobilenet

plt.figure(figsize=(9,9))
sns.heatmap(cf_matrix_mobilenet, cbar=False, fmt='d', annot=True, cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix of the CNN Classifier')
plt.show()

"""# Densenet-121 Training and Inference"""

bifurcation(models.densenet121)

model_densenet121, loss_densenet121, optim_densenet121 = selective_finetuning_single_layer(models.densenet121, 'classifier')
model_densenet121 ,densenet121_train ,densenet121_test, densenet121_pred, densenet121_true = model(train,test,5,model_densenet121, loss_densenet121, optim_densenet121)

cf_matrix_densenet=confusion_matrix(densenet121_true,densenet121_pred)
cf_matrix_densenet

plt.figure(figsize=(9,9))
sns.heatmap(cf_matrix_densenet, cbar=False, fmt='d', annot=True, cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix of the CNN Classifier')
plt.show()

"""# Efficientnet-B0 Training and Inference"""

bifurcation(models.efficientnet.efficientnet_b0)

model_efficientnet_b0, loss_efficientnet_b0, optim_efficientnet_b0 = selective_finetuning_single_layer(models.efficientnet_b0, 'classifier')
model_efficientnet_b0 ,efficientnet_b0_train ,efficientnet_b0_test, efficientnet_b0_pred, efficientnet_b0_true = model(train,test,5,model_efficientnet_b0, loss_efficientnet_b0, optim_efficientnet_b0)

cf_matrix_efficientnet_b0=confusion_matrix(efficientnet_b0_true,efficientnet_b0_pred)
cf_matrix_efficientnet_b0

plt.figure(figsize=(9,9))
sns.heatmap(cf_matrix_efficientnet_b0, cbar=False, fmt='d', annot=True, cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix of the CNN Classifier')
plt.show()

"""# Alexnet Training and Inference"""

bifurcation(models.alexnet)

model_alexnet, loss_alexnet, optim_alexnet = selective_finetuning_single_layer(models.alexnet, 'classifier')
model_alexnet ,alexnet_train ,alexnet_test, alexnet_pred, alexnet_true = model(train,test,5,model_alexnet, loss_alexnet, optim_alexnet)

cf_matrix_alexnet=confusion_matrix(alexnet_true,alexnet_pred)
cf_matrix_alexnet

plt.figure(figsize=(9,9))
sns.heatmap(cf_matrix_alexnet, cbar=False, fmt='d', annot=True, cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix of the CNN Classifier')
plt.show()

"""# ResNet18 Training and Inference"""

bifurcation(models.resnet18)

model_resnet18, loss_resnet18, optim_resnet18 = selective_finetuning_single_layer(models.resnet18, 'fc')
model_resnet18 ,resnet18_train ,resnet18_test, resnet18_pred, resnet18_true = model(train,test,5,model_resnet18, loss_resnet18, optim_resnet18)

cf_matrix_resnet18=confusion_matrix(resnet18_true,resnet18_pred)
cf_matrix_resnet18

plt.figure(figsize=(9,9))
sns.heatmap(cf_matrix_resnet18, cbar=False, fmt='d', annot=True, cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix of the CNN Classifier')
plt.show()

"""# Loss v/s Epochs and Accuracy v/s Epochs Curves"""

plt.figure(figsize=(10,5))
plt.plot([j for j in range(1,6)],[resnet18_train[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[vgg16_train[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[densenet121_train[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[mobilenet_v3_small_train[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[efficientnet_b0_train[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[alexnet_train[i][1] for i in range(0,5)])
plt.xlabel("Epochs")
plt.ylabel("Average Loss")
plt.title("Loss v/s Epochs for Training")
plt.legend(["ResNet18","VGG16","DenseNet121","Mobilenet_v3_small","Efficientnet_b0","Alexnet"])
plt.show()

plt.figure(figsize=(10,5))
plt.plot([j for j in range(1,6)],[resnet18_test[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[vgg16_test[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[densenet121_test[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[mobilenet_v3_small_test[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[efficientnet_b0_test[i][1] for i in range(0,5)])
plt.plot([j for j in range(1,6)],[alexnet_test[i][1] for i in range(0,5)])
plt.xlabel("Epochs")
plt.ylabel("Average Loss")
plt.title("Loss v/s Epochs for Testing")
plt.legend(["ResNet18","VGG16","DenseNet121","Mobilenet_v3_small","Efficientnet_b0","Alexnet"])
plt.show()

plt.figure(figsize=(10,5))
plt.plot([j for j in range(1,6)],[resnet18_train[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[vgg16_train[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[densenet121_train[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[mobilenet_v3_small_train[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[efficientnet_b0_train[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[alexnet_train[i][2].cpu().numpy() for i in range(0,5)])
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.title("Accuracy v/s Epochs for Training")
plt.legend(["ResNet18","VGG16","DenseNet121","Mobilenet_v3_small","Efficientnet_b0","Alexnet"])
plt.show()

plt.figure(figsize=(10,5))
plt.plot([j for j in range(1,6)],[resnet18_test[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[vgg16_test[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[densenet121_test[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[mobilenet_v3_small_test[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[efficientnet_b0_test[i][2].cpu().numpy() for i in range(0,5)])
plt.plot([j for j in range(1,6)],[alexnet_test[i][2].cpu().numpy() for i in range(0,5)])
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.title("Accuracy v/s Epochs for Testing")
plt.legend(["ResNet18","VGG16","DenseNet121","Mobilenet_v3_small","Efficientnet_b0","Alexnet"])
plt.show()

"""#Wandb Saves"""

import wandb

torch.save(model_vgg16, '/content/drive/MyDrive/DL_Project_2/model_vgg16.pth')
run = wandb.init(project='DL_Project_2')
artifact = wandb.Artifact('VGG16', type='VGG16')
artifact.add_file('/content/drive/MyDrive/DL_Project_2/model_vgg16.pth')
run.log_artifact(artifact)
run.join()

torch.save(model_alexnet, '/content/drive/MyDrive/DL_Project_2/model_alexnet.pth')
run = wandb.init(project='DL_Project_2')
artifact = wandb.Artifact('alexnet', type='alexnet')
artifact.add_file('/content/drive/MyDrive/DL_Project_2/model_alexnet.pth')
run.log_artifact(artifact)
run.join()

torch.save(model_efficientnet_b0, '/content/drive/MyDrive/DL_Project_2/model_efficientnet_b0.pth')
run = wandb.init(project='DL_Project_2')
artifact = wandb.Artifact('efficientnet_b0', type='efficientnet_b0')
artifact.add_file('/content/drive/MyDrive/DL_Project_2/model_efficientnet_b0.pth')
run.log_artifact(artifact)
run.join()

torch.save(model_mobilenet_v3_small, '/content/drive/MyDrive/DL_Project_2/model_mobilenet_v3_small.pth')
run = wandb.init(project='DL_Project_2')
artifact = wandb.Artifact('mobilenet_v3_small', type='mobilenet_v3_small')
artifact.add_file('/content/drive/MyDrive/DL_Project_2/model_mobilenet_v3_small.pth')
run.log_artifact(artifact)
run.join()

torch.save(model_resnet18, '/content/drive/MyDrive/DL_Project_2/model_resnet18.pth')
run = wandb.init(project='DL_Project_2')
artifact = wandb.Artifact('resnet18', type='resnet18')
artifact.add_file('/content/drive/MyDrive/DL_Project_2/model_resnet18.pth')
run.log_artifact(artifact)
run.join()

torch.save(model_densenet121, '/content/drive/MyDrive/DL_Project_2/model_densenet121.pth')
run = wandb.init(project='DL_Project_2')
artifact = wandb.Artifact('densenet121', type='densenet121')
artifact.add_file('/content/drive/MyDrive/DL_Project_2/model_densenet121.pth')
run.log_artifact(artifact)
run.join()

!pip install wandb

"""# End-To-End Pipeline"""

path = input("Enter the File-Path for 10-Seconds Hindi-Music Based Emotion Classification :- ")
input_audio , y = lib.load(path)
hl = 512 # number of samples per time-step in spectrogram
hi = 224 # Height of image
wi = 224 # Width of image
audio_window = input_audio[0:wi*hl]
spectrogram = lib.feature.melspectrogram(y=audio_window, sr=y, n_mels=hi, fmax=8000, hop_length=hl)
plot = lib.power_to_db(spectrogram, ref=np.max)
plt.imshow(plot)
final_plot = cv2.resize(cv2.cvtColor(plot,cv2.COLOR_GRAY2RGB),(224,224))

print(" ")
print("Pre-Trained Models List\n")
print("1. Alexnet\n")
print("2. EfficientNet-B0\n")
print("3. ResNet18\n")
print("4. VGG16\n")
print("5. MobileNet_V3_Small\n")
print("6. DenseNet121\n\n")
model_choice = int(input("Enter the Choice of Model :- \n"))
if model_choice==1:
  model = torch.load('/content/drive/MyDrive/DL_Project_2/model_alexnet.pth', map_location='cuda:0')
if model_choice==2:
  model = torch.load('/content/drive/MyDrive/DL_Project_2/model_eddicientnet_b0.pth', map_location='cuda:0')
if model_choice==3:
  model = torch.load('/content/drive/MyDrive/DL_Project_2/model_resnet18.pth', map_location='cuda:0')
if model_choice==4:
  model = torch.load('/content/drive/MyDrive/DL_Project_2/model_vgg16.pth', map_location='cuda:0')
if model_choice==5:
  model = torch.load('/content/drive/MyDrive/DL_Project_2/model_mobilenet_v3_small.pth', map_location='cuda:0')
if model_choice==6:
  model = torch.load('/content/drive/MyDrive/DL_Project_2/model_densenet121.pth', map_location='cuda:0')

class_map = {0:'Sad',1:'Romantic',2:'Devotional',3:'Party',4:'Happy'}
model_input = transforms.Compose([transforms.ToTensor(),transforms.Normalize((0,0,0), (1,1,1))])(final_plot)[None]
with torch.no_grad():
  output = model(model_input.cuda())
  class_predict = output.data.max(1, keepdim=True)[1]
  print("\nPredicted Emotion -->"+class_map[class_predict.cpu().numpy()[0][0]])

