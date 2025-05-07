import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, SAGEConv


num_users = 631
num_posts=1210


class GNNRecommender(torch.nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.emb_user = torch.nn.Embedding(num_users, hidden_dim)
        self.emb_post = torch.nn.Embedding(num_posts, hidden_dim)

        self.conv1 = HeteroConv({
            ('user','viewed','post'): SAGEConv(hidden_dim, hidden_dim),
            ('post','rev_viewed','user'): SAGEConv(hidden_dim, hidden_dim),
            ('user','liked','post'): SAGEConv(hidden_dim, hidden_dim),
            ('post','rev_liked','user'): SAGEConv(hidden_dim, hidden_dim),
        }, aggr='sum')

        self.conv2 = HeteroConv({
            ('user','viewed','post'): SAGEConv(hidden_dim, hidden_dim),
            ('post','rev_viewed','user'): SAGEConv(hidden_dim, hidden_dim),
            ('user','liked','post'): SAGEConv(hidden_dim, hidden_dim),
            ('post','rev_liked','user'): SAGEConv(hidden_dim, hidden_dim),
        }, aggr='sum')

    def forward(self, data):
        x_dict = {
            'user': self.emb_user.weight,
            'post': self.emb_post.weight
        }
        x_dict = self.conv1(x_dict, data.edge_index_dict)
        x_dict = {k: F.relu(v) for k,v in x_dict.items()}
        x_dict = self.conv2(x_dict, data.edge_index_dict)
        return x_dict

    def decode(self, user_emb, post_emb, edge_index):
        u, p = edge_index
        return (user_emb[u] * post_emb[p]).sum(dim=1)