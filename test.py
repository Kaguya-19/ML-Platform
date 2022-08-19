import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import torchvision
from torchvision import datasets, transforms
from torch.autograd import Variable
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
batch_size = 64
learning_rate = 0.001
# 将数据处理成Variable, 如果有GPU, 可以转成cuda形式


def get_variable(x):
    x = Variable(x)
    return x.cuda() if torch.cuda.is_available() else x


train_dataset = datasets.MNIST(
    root='./mnist/',
    train=True,
    transform=transforms.ToTensor(),
    download=True)
transforms = transforms.Compose([transforms.ToTensor(),
                                 transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])])
train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                           batch_size=batch_size,
                                           shuffle=True)
images, labels = next(iter(train_loader))
img = torchvision.utils.make_grid(images)
img = img.numpy().transpose(1, 2, 0)
print(labels)
plt.imshow(img)
plt.show()


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # 使用序列工具快速构建
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.fc = nn.Linear(7 * 7 * 32, 10)

    def forward(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        out = out.view(out.size(0), -1)  # reshape
        out = self.fc(out)
        return out


cnn = CNN()
if torch.cuda.is_available():
    cnn = cnn.cuda()
loss_func = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(cnn.parameters(), lr=learning_rate)
print(cnn)
num_epochs = 2
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        images = get_variable(images)
        labels = get_variable(labels)
        outputs = cnn(images)
        optimizer.zero_grad()
        loss = loss_func(outputs, labels)
        loss.backward()  # 反向传播，自动计算每个节点的锑度至
        optimizer.step()
        if (i + 1) % 100 == 0:
            print('Epoch [%d/%d], Iter [%d/%d] Loss: %.4f'
                  % (epoch + 1, num_epochs, i + 1, len(train_dataset) // batch_size, loss.item()))
# Save the Trained Model
torch.save(cnn, 'cnn.pt')
