import numpy as np
import matplotlib.pyplot as plt

folder_path = os.getenv('FOLDER_PATH')

def load_dataset():
    with np.load(f"{folder_path}/mnist.npz") as f:
        x_train = f['x_train'].astype("float") / 255
        
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1] * x_train.shape[2]))
        
        y_train = f['y_train']

        y_train = np.eye(10)[y_train]

        return x_train, y_train


images, labels = load_dataset()

weights_input_to_hidden = np.random.uniform(-0.5, 0.5, (20, 784))
weights_hidden_to_output = np.random.uniform(-0.5, 0.5, (10, 20))

bias_input_to_hidden = np.zeros((20, 1))
bias_hidden_to_output = np.zeros((10, 1))

epochs = 4
e_loss = 0
e_correct = 0
learning_rate = 0.01

for epoch in range(epochs):
    print(f"Epoch #{epoch}")

    for image, label in zip(images, labels):
        image = np.reshape(image, (-1, 1))
        label = np.reshape(label, (-1, 1))

        hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ image
        hidden = 1 / (1 + np.exp(-hidden_raw))

        output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
        output = 1 / (1 + np.exp(-output_raw))

        e_loss += 1 / len(output) * np.sum((output - label) ** 2, axis=0)
        e_correct += int(np.argmax(output) == np.argmax(label))

        delta_output = output - label
        weights_hidden_to_output += -learning_rate * delta_output @ np.transpose(hidden)
        bias_hidden_to_output += -learning_rate * delta_output

        delta_hidden = np.transpose(weights_hidden_to_output) @ delta_output * (hidden * (1 - hidden))
        weights_input_to_hidden += -learning_rate * delta_hidden @ np.transpose(image)
        bias_input_to_hidden += -learning_rate * delta_hidden

    print(f"Loss: {round((e_loss[0] / images.shape[0]) * 100, 3)}%")
    print(f"Accuracy: {round((e_correct / images.shape[0]) * 100, 3)}%")
    e_loss = 0
    e_correct = 0

img = plt.imread(f"{folder_path}/AgACAgIAAxkBAANDZl9hL_-uQYwiVKsSRsnyDP1q3dMAAjz2MRtsxPlKCHEQqzY32A8BAAMCAANtAAM1BA.jpg", format="jpeg")

gray = lambda rgb : np.dot(rgb[... , :3], [0.299, 0.587, 0.114])
img = 1 - (gray(img).astype("float32") / 255)

img = np.reshape(img, (img.shape[0]) * img.shape[1])

img = np.reshape(img, (-1, 1))

hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ image
hidden = 1 / (1 + np.exp(-hidden_raw))

output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
output = 1 / (1 + np.exp(-output_raw))


plt.imshow(img.reshape(28, 28), cmap="Greys")
plt.title(f"NN suggests the CUSTOM number is: {output.argmax()}")
plt.show()