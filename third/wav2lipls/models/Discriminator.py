import torch
from torch import nn
import torch.nn.functional as F
from torch.nn.utils.parametrizations import spectral_norm


class DownBlock2d(nn.Module):
    def __init__(self, in_features, out_features, kernel_size=4, pool=False):
        super(DownBlock2d, self).__init__()
        self.conv = spectral_norm(nn.Conv2d(in_channels=in_features, out_channels=out_features, kernel_size=kernel_size))
        self.pool = pool

    def forward(self, x):
        out = x
        out = self.conv(out)
        out = F.leaky_relu(out, 0.2)
        if self.pool:
            out = F.avg_pool2d(out, (2, 2))
        return out


class Discriminator(nn.Module):
    """
    Discriminator for GAN loss
    """

    def __init__(self, num_channels, block_expansion=64, num_blocks=4, max_features=512, is_2d=False, is_sync=False):
        super(Discriminator, self).__init__()
        down_blocks = []
        for i in range(num_blocks):
            down_blocks.append(
                DownBlock2d(num_channels if i == 0 else min(max_features, block_expansion * (2 ** i)),
                            min(max_features, block_expansion * (2 ** (i + 1))),
                            kernel_size=4, pool=(i != num_blocks - 1)))
        self.down_blocks = nn.ModuleList(down_blocks)
        self.conv = spectral_norm(nn.Conv2d(self.down_blocks[-1].conv.out_channels, out_channels=1, kernel_size=1))
        self.is_2d = is_2d
        self.is_sync = is_sync

    def to_2d(self, face_sequences):
        B = face_sequences.size(0)
        face_sequences = torch.cat([face_sequences[:, :, i] for i in range(face_sequences.size(2))], dim=0)
        return face_sequences

    def to_sync(self, face_sequences):
        B = face_sequences.size(0)
        face_sequences = torch.cat([face_sequences[:, :, i] for i in range(face_sequences.size(2))], dim=1)
        return face_sequences

    def forward(self, x):

        if self.is_2d and self.is_sync:
            raise Exception("is_2d和is_sync不可以同时为True")

        if self.is_2d:
            x = self.to_2d(x)

        if self.is_sync:
            x = self.to_sync(x)

        feature_maps = []
        out = x
        for down_block in self.down_blocks:
            feature_maps.append(down_block(out))
            out = feature_maps[-1]
        out = self.conv(out)
        return feature_maps, out
