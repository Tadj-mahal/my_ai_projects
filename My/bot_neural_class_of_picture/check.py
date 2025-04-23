import torch

# Создаем тензор на GPU
x = torch.randn(3, 3).to("cuda")
y = torch.randn(3, 3).to("cuda")

# Выполняем операцию на GPU
z = x + y

print(z)
