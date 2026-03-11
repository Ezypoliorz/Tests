import torch
import torch.nn as nn
import torch.optim as optim

class NeuralNetwork(nn.Module) :
    def __init__(self) :
        super(NeuralNetwork, self).__init__()

        # Defining the layers
        self.hiddenLayer = nn.Linear(2, 4) # 2 inputs, 4 hidden neurons

        # Activating Sigmoid to introduce non-linearity
        self.activation = nn.Sigmoid()

        # Defining output layer
        self.outputLayer = nn.Linear(4, 1) # 4 inputs (from the previous hidden layer), 1 output
    
    def forward(self, x) :
        # Defining data forwarding
        x = self.hiddenLayer(x)
        x = self.activation(x)
        x = self.outputLayer(x)

        return x

model = NeuralNetwork()

# Test data 1
# We want [1, 0] to output 1, and [0, 1] to output 0
X = torch.tensor([[1.0, 0.0], [0.0, 1.0]], dtype=torch.float32)
Y = torch.tensor([[1.0], [0.0]], dtype=torch.float32)

# Defining the loss function
criteria = nn.MSELoss()

# Defining the optimizer (Gradient descent : SGD)
optimizer = optim.SGD(model.parameters(), lr=0.1) # lr : learning rate

for step in range(1000) :
    # Resetting the gradients
    optimizer.zero_grad()

    predictions = model(X)

    # Calculating the loss
    loss = criteria(predictions, Y)

    # Calculating the gradients
    loss.backward()

    # Updating the weights
    optimizer.step()

    if step % 200 == 0:
        print(f"Step {step}, Loss : {loss.item():.4f}")

print("Training complete !")

# Switching to evaluation mode
model.eval()

# Defining new data, never seen by the model
newData = torch.tensor([[0.9, 0.1]], dtype=torch.float32)

# Predicting the result without updating the gradient
with torch.no_grad():
    rawPrediction = model(newData)
    
# Interpretating the result
finalResult = 1 if rawPrediction.item() > 0.5 else 0 # If the output is > 0.5, we consider it as class 1, else 0

print(f"Raw prediction (probability) : {rawPrediction.item():.4f}")
print(f"Predicted class : {finalResult}")