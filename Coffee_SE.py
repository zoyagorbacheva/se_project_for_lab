# -*- coding: utf-8 -*-
"""Coffee_PE.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eF7IfJJiu9tb0h9eFY7bAcdA_-dyA9dV

# Тема: Нейронная сеть классифицирует зерна кофе по степени обжарки по их изображению.
"""

from PIL import Image
from pathlib import Path
import random
import os

"""Загрузим датасет:"""

p=Path('Coffee Bean Dataset/')

im_path = []
for dirpath, dirnames, filenames in os.walk(p):
    for filename in filenames:
        im_path.append(os.path. join(dirpath, filename))
im_path

"""Проанализируем датасет:"""

len(im_path)

test_count = 0
train_count = 0
for x in range(len(im_path)):
    if im_path[x].split('\\')[1] == 'test':
        test_count += 1
    if im_path[x].split('\\')[1] == 'train':
        train_count += 1
print(test_count)
print(train_count)

"""Посмотрим на примеры изображений из датасета:"""

path = random.choice(im_path)
img = Image.open(path)
cl = path.split('\\')[-2]
print(cl)
img

path = random.choice(im_path)
img = Image.open(path)
cl = path.split('\\')[-2]
print(cl)
img

import numpy as np
import matplotlib.pyplot as plt

"""Узнаем размер изображений в датасете и какие бывают типы обжарки (Light, Green, Medium, Dark):"""

arr = np.asarray(img)
plt.figure(figsize=(5, 3.5))
plt.imshow(arr)
plt.title(f'Image class: {cl} | image shape {arr.shape}')
plt.axis(False);

cl_names = []
for dirpath, dirnames, filenames in os.walk('Coffee Bean Dataset/train'):
    for dirname in dirnames:
        if dirname not in cl_names:
            cl_names.append(dirname)
cl_names

"""Разобьем датасет на обучающую и тестовую выборку:"""

files_num = 0
sp_tr = []
for i in cl_names:
    for x in os. listdir('Coffee Bean Dataset/train/' + i):
        files_num += 1
    sp_tr.append(files_num)
    files_num=0
sp_test = []
for i in cl_names:
    for x in os. listdir('Coffee Bean Dataset/test/' + i):
        files_num += 1
    sp_test.append(files_num)
    files_num=0
print(sp_tr)
print(sp_test)

import pandas as pd

df = pd.DataFrame()
df['Class_names'] = cl_names
df['Train_count'] = sp_tr
df['Test_count'] = sp_test
df

df.describe()

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

"""Изменим размеры изображений в датасете:"""

data_transform = transforms. Compose([
transforms.Resize(size=(64, 64)),
transforms. RandomHorizontalFlip(p=0.5),
transforms. ToTensor()
])

data_transform(img).shape

img

plt.figure(figsize=(3,2))
plt.imshow(data_transform(img).permute(1, 2, 0));

train_data = datasets. ImageFolder(root='Coffee Bean Dataset/train',
transform=data_transform,
target_transform=None)
test_data = datasets.ImageFolder(root='Coffee Bean Dataset/test',
transform=data_transform)

train_data

test_data

"""Зададим классам числовые индексы:"""

class_names = train_data.classes
class_names

class_dict = train_data.class_to_idx
class_dict

"""Пример векторизации изображения:"""

batch_size = 32
train_DL = DataLoader(dataset=train_data,
                    batch_size=batch_size,
                    num_workers=os.cpu_count(),
                    shuffle=True)
test_DL = DataLoader(dataset=test_data,
                    batch_size=batch_size,
                    num_workers=os.cpu_count(),
                    shuffle=False)

img, label = next(iter(train_DL))
print(img.shape)
print(label.shape)

img

label

"""Модель:"""

class Pict_cl_1(torch.nn.Module):
    def __init__(self, inp, out, hidden_units):
        super().__init__()
        self.conv_1 = torch.nn.Sequential(
        torch.nn.Conv2d(in_channels=inp, out_channels=hidden_units,
                kernel_size=3, stride=1, padding=1),
        torch.nn.ReLU(),
        torch.nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units,
                kernel_size=3, stride=1, padding=1),
        torch.nn.MaxPool2d(kernel_size=2))
        self.conv_2 = torch.nn.Sequential(
        torch.nn.Conv2d(in_channels=hidden_units,
                out_channels=hidden_units, kernel_size=3,
                stride=1, padding=1),
        torch.nn.ReLU(),
        torch.nn.Conv2d(in_channels=hidden_units,
                out_channels=hidden_units, kernel_size=3,
                stride=1, padding=1),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(kernel_size=2))

        self.classifier = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(in_features=hidden_units*16*16,
                            out_features=out),
            torch.nn.Softmax(dim=1)
        )
    def forward(self, x):
        x = self.conv_1(x)
        x = self.conv_2(x)
        x = self.classifier(x)
        return x

torch.manual_seed(15)
mod_1 = Pict_cl_1(inp=3, out=len(class_names), hidden_units=15)

from sklearn.metrics import accuracy_score as acc

"""Вспомогательные функции для обучения:"""

def train_step(model: torch.nn.Module,
            dataloader: torch.utils.data.DataLoader,
            loss_fn: torch.nn.Module,
            optimizer: torch.optim.Optimizer):

    train_loss, train_acc = 0, 0

    for x, y in dataloader:
        model.train()
        y_logits = model(x)
        loss=loss_fn(y_logits, y)
        train_loss += loss
        train_acc += acc(y, y_logits.argmax(dim=1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    train_loss /= len(dataloader)
    train_acc /= len(dataloader)
    return train_loss, train_acc

def test_step(model: torch.nn.Module,
            dataloader: torch.utils.data.DataLoader,
            loss_fn: torch.nn.Module):

    model.eval()
    test_loss, test_acc = 0, 0

    with torch.inference_mode():
        for x_test, y_test in dataloader:
            test_logits = model(x_test)
            test_loss += loss_fn(test_logits, y_test)
            test_acc += acc(y_test, test_logits.argmax(dim=1))
        test_loss /= len(dataloader)
        test_acc /= len(dataloader)
    return test_loss, test_acc

def train_nn(model: torch.nn.Module,
            train_DL: torch.utils.data.DataLoader,
            test_DL: torch.utils.data.DataLoader,
            loss_fn: torch.nn.Module,
            optimizer: torch.optim.Optimizer,
            epochs: int):

    res = {'train_loss': [],
            'train_acc': [],
            'test_loss': [],
            'test_acc': []}

    for i in range(epochs):
        train_loss, train_acc = train_step(model=model,
                                            dataloader=train_DL,
                                            loss_fn=loss_fn,
                                            optimizer=optimizer)
        test_loss, test_acc = test_step(model=model,
                                        dataloader=test_DL,
                                        loss_fn=loss_fn)
        print(f'Epoch: {i} | Train_loss: {train_loss: .4f} | Train_acc: {train_acc: .4f}')
        print(f'Evaluation | Test_loss: {test_loss :.4f} | Test_acc: {test_acc: .4f}')
        print()

        res['train_loss'].append(train_loss)
        res['train_acc'].append(train_acc)
        res['test_loss' ].append(test_loss)
        res['test_acc'].append(test_acc)
    return res

"""Обучаем модель:"""

mod_1_res = train_nn(model=mod_1,
                    train_DL=train_DL, test_DL=test_DL,
                    loss_fn=torch.nn.CrossEntropyLoss(),
                    optimizer=torch.optim.Adam(params=mod_1.parameters(),
                                                lr=0.001),
                    epochs=24)
mod_1_res

"""Оценим качество обучения

accuracy на test: 0.96

Построим график потерь:
"""

tr_loss = np.array(torch.tensor(mod_1_res['train_loss']))
test_loss = np.array(torch.tensor(mod_1_res['test_loss']))
plt.plot(tr_loss, c='b', label='Train_loss')
plt.plot(test_loss, c='r', label = 'Test_loss')
plt.xlabel('Epochs')
plt.ylabel('Loss_values')
plt.legend();

"""Построим график для accuracy во время обучения модели на разных эпохах:"""

tr_acc = np.array(torch.tensor(mod_1_res['train_acc']))
test_acc = np.array(torch.tensor(mod_1_res['test_acc']))
plt.plot(tr_acc, c='b', label='Train_acc')
plt.plot(test_acc, c='r', label = 'Test_acc')
plt.xlabel('Epochs')
plt.ylabel('Loss_values')
plt.legend();

"""Посмотрим, что выдает модель:"""

mod_1(img)

mod_1(img).shape

"""Проверка работы:"""

import torchvision
transform = transforms. Compose([transforms.Resize(size=(64, 64), antialias=None)])

"""Изображение из датасета:"""

test_img1 = torchvision.io.read_image('с1.jpg').type(torch.int)
plt.imshow(test_img1.permute(1,2,0))

tr_test_img1 = transform(test_img1.type(torch.float32))
tr_test_img1.shape

mod_1.eval()
with torch.inference_mode():
    pred = mod_1(tr_test_img1.unsqueeze(0))
class_names[pred.argmax(dim=1)]

"""Изображение из интернета:"""

test_img2 = torchvision.io.read_image('c4.jpg').type(torch.int)
plt.imshow(test_img2.permute(1,2,0))

tr_test_img2 = transform(test_img2.type(torch.float32))
tr_test_img2.shape

mod_1.eval()
with torch.inference_mode():
    pred = mod_1(tr_test_img2.unsqueeze(0))
class_names[pred.argmax(dim=1)]