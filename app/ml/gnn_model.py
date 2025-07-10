import torch
import torch.nn as nn
import torch.nn.functional as F

class ContentEmbeddingModel(nn.Module):
    """Simple neural network for content embedding"""
    def __init__(self, input_dim, hidden_dim=128, output_dim=64):
        super(ContentEmbeddingModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return F.normalize(x, p=2, dim=1) 