# A simple neural network test with PyTorch
# Recognises numbers on the images of the PyTorch dataset

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import random
import matplotlib.pyplot as plt

# Converts the images to Tensors, and normalizes the colors
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])

# Downloads the dataset
trainSet = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)

# Loads the images by batches so teh RAM isn't saturated
trainLoader = torch.utils.data.DataLoader(trainSet, batch_size=64, shuffle=True)

class DigitClassifier(nn.Module) :
    def __init__(self):
        super(DigitClassifier, self).__init__()
        # Flattens the image (28x28px) to a vector (784px)
        self.flatten = nn.Flatten()
        # Input layers : 784 neurons - Hidden layers : 128 neurons
        self.fc1 = nn.Linear(784, 128)
        # Activates the network
        self.relu = nn.ReLU()
        # Output layer : 10 values (0 to 9)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

model = DigitClassifier()

# Sets up the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
print("Starting training...")
for epoch in range(10) :
    running_loss = 0.0
    for images, labels in trainLoader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    
    print(f"Epoch {epoch+1} - Average loss : {running_loss/len(trainLoader):.4f}")

print("Traning done !")

# Fetches the dataset for testing
testSet = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
testImage, realLabel = testSet[random.randint(0, len(testSet) - 1)]

model.eval()
with torch.no_grad():
    rawPrediction = model(testImage.unsqueeze(0))
    # Returns the index of the highest score (most probable)
    predictedNumber = torch.argmax(rawPrediction, dim=1).item()

visualizationImage = testImage * 0.5 + 0.5

# Converts the tensor to a NumPy array, and removing the color
visualizationImage = visualizationImage.numpy().squeeze()

# Display
plt.imshow(visualizationImage, cmap='gray')
plt.title(f"Actual number : {realLabel} | Predicted : {predictedNumber}")
plt.axis('off') # Hides the x and y axis
plt.show()